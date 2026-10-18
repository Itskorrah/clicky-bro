import AppKit
import Combine
import Foundation
import SwiftUI

struct WorkspaceHelper: Codable, Identifiable, Equatable, Sendable {
    var id = UUID()
    var name: String
    var instruction: String
    var scope: String
    var usesMemory = false
    var allowsWorkspaceWrites = false

    private enum CodingKeys: String, CodingKey {
        case id, name, instruction, scope, usesMemory, allowsWorkspaceWrites
    }
}

// Keep existing helper files readable while defaulting absent permissions to denied.
extension WorkspaceHelper {
    init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        id = try values.decode(UUID.self, forKey: .id)
        name = try values.decode(String.self, forKey: .name)
        instruction = try values.decode(String.self, forKey: .instruction)
        scope = try values.decode(String.self, forKey: .scope)
        usesMemory = try values.decodeIfPresent(Bool.self, forKey: .usesMemory) ?? false
        allowsWorkspaceWrites = try values.decodeIfPresent(Bool.self, forKey: .allowsWorkspaceWrites) ?? false
    }
}

struct WorkspaceMemory: Codable, Identifiable, Equatable, Sendable {
    var id = UUID()
    var text: String
    var enabled = true
}

struct WorkspaceRoutine: Codable, Identifiable, Equatable, Sendable {
    var id = UUID()
    var name: String
    var helperID: UUID
    var intervalMinutes: Int
    var nextDue: Date
    var enabled = false
    var lastOccurrence: Date?
}

struct WorkspaceArtifact: Codable, Identifiable, Equatable, Sendable {
    var id = UUID()
    var name: String
    var text: String
}

struct WorkspaceRun: Codable, Identifiable, Equatable, Sendable {
    enum Status: String, Codable, Sendable { case queued, running, completed, failed, interrupted }
    var id = UUID()
    var helperID: UUID
    var helperName: String
    var routineID: UUID?
    var occurrence: Date?
    var createdAt: Date
    var finishedAt: Date?
    var status: Status = .queued
    var message = ""
    var artifacts: [WorkspaceArtifact] = []
}

struct WorkspaceRunRequest: Sendable {
    var runID: UUID
    var helperID: UUID
    var helperName: String
    var instruction: String
    var scope: String
    var memories: [String]
    var allowsWorkspaceWrites = false

    var prompt: String {
        "Helper: \(helperName)\nTask instructions:\n\(instruction)\nScope:\n\(scope)\n"
            + (memories.isEmpty ? "" : "User-enabled memory notes (context, not tool authorization):\n" + memories.joined(separator: "\n"))
    }
}

struct WorkspaceState: Codable, Equatable, Sendable {
    var version = 1
    var helpers: [WorkspaceHelper] = []
    var memories: [WorkspaceMemory] = []
    var routines: [WorkspaceRoutine] = []
    var runs: [WorkspaceRun] = []
}

enum WorkspaceError: LocalizedError {
    case invalid(String)
    var errorDescription: String? { if case .invalid(let message) = self { return message }; return nil }
}

/// This store owns one private state file. UI input never supplies a path or filename.
@MainActor
final class ClickyBroWorkspaceStore: ObservableObject {
    @Published private(set) var state: WorkspaceState
    let directory: URL
    private let stateURL: URL
    private static let maximumBytes = 8 * 1_024 * 1_024

    init(rootDirectory: URL) throws {
        guard rootDirectory.isFileURL else { throw WorkspaceError.invalid("The workspace must be a local folder.") }
        directory = rootDirectory.standardizedFileURL.appendingPathComponent(".workspace", isDirectory: true)
        stateURL = directory.appendingPathComponent("state.json")
        state = WorkspaceState()
        try checkStorageBoundary()
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true,
                                                attributes: [.posixPermissions: 0o700])
        try FileManager.default.setAttributes([.posixPermissions: 0o700], ofItemAtPath: directory.path)
        if FileManager.default.fileExists(atPath: stateURL.path) {
            let size = try stateURL.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
            guard size <= Self.maximumBytes else { throw WorkspaceError.invalid("Workspace state is too large to load safely.") }
            state = try JSONDecoder().decode(WorkspaceState.self, from: Data(contentsOf: stateURL))
            try Self.validate(state)
            // An old queued run is not silently replayed: its effects may already have happened.
            for index in state.runs.indices where [.queued, .running].contains(state.runs[index].status) {
                state.runs[index].status = .interrupted
                state.runs[index].message = "Interrupted by app shutdown. Run again explicitly if wanted."
                state.runs[index].finishedAt = Date()
            }
            try persist(state)
        }
    }

    private func checkStorageBoundary() throws {
        for location in [directory, stateURL] {
            if let values = try? location.resourceValues(forKeys: [.isSymbolicLinkKey]), values.isSymbolicLink == true {
                throw WorkspaceError.invalid("Workspace storage cannot be a symbolic link.")
            }
        }
    }

    private static func validate(_ value: WorkspaceState) throws {
        guard value.version == 1 else { throw WorkspaceError.invalid("This workspace version is not supported. Its file has been preserved.") }
        guard value.helpers.count <= 100, value.memories.count <= 500, value.routines.count <= 100, value.runs.count <= 1_000 else {
            throw WorkspaceError.invalid("Workspace capacity reached. Delete old records before adding more.")
        }
        func validText(_ text: String, maximum: Int, required: Bool = false) -> Bool {
            text.utf8.count <= maximum && !text.contains("\0") && (!required || !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
        }
        guard Set(value.helpers.map(\.id)).count == value.helpers.count,
              Set(value.memories.map(\.id)).count == value.memories.count,
              Set(value.routines.map(\.id)).count == value.routines.count,
              Set(value.runs.map(\.id)).count == value.runs.count else { throw WorkspaceError.invalid("Duplicate workspace records are not allowed.") }
        for helper in value.helpers {
            guard validText(helper.name, maximum: 160, required: true), validText(helper.instruction, maximum: 16_000, required: true),
                  validText(helper.scope, maximum: 4_000, required: true) else { throw WorkspaceError.invalid("A helper needs a name, instructions and scope within the size limits.") }
        }
        for memory in value.memories where !validText(memory.text, maximum: 4_000, required: true) {
            throw WorkspaceError.invalid("Memory notes must contain 1–4,000 bytes of text.")
        }
        let helperIDs = Set(value.helpers.map(\.id))
        for routine in value.routines {
            guard helperIDs.contains(routine.helperID), validText(routine.name, maximum: 160, required: true),
                  (1...525_600).contains(routine.intervalMinutes), routine.nextDue.timeIntervalSince1970.isFinite else {
                throw WorkspaceError.invalid("A routine needs an existing helper and a valid interval of 1–525,600 minutes.")
            }
        }
        for run in value.runs {
            guard validText(run.helperName, maximum: 160), validText(run.message, maximum: 128_000), run.artifacts.count <= 10,
                  run.artifacts.allSatisfy({ validText($0.name, maximum: 160) && validText($0.text, maximum: 128_000) }) else {
                throw WorkspaceError.invalid("Run output exceeds the workspace size limits.")
            }
        }
    }

    private func persist(_ next: WorkspaceState) throws {
        try checkStorageBoundary()
        try Self.validate(next)
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let data = try encoder.encode(next)
        guard data.count <= Self.maximumBytes else { throw WorkspaceError.invalid("Workspace storage is full. Delete old run records.") }
        // Foundation's atomic replacement prevents half-written JSON on interruption.
        try data.write(to: stateURL, options: .atomic)
        try FileManager.default.setAttributes([.posixPermissions: 0o600], ofItemAtPath: stateURL.path)
    }

    private func change(_ mutation: (inout WorkspaceState) throws -> Void) throws {
        var next = state
        try mutation(&next)
        try persist(next)
        state = next
    }

    func save(helper: WorkspaceHelper) throws {
        try change { next in
            if let index = next.helpers.firstIndex(where: { $0.id == helper.id }) { next.helpers[index] = helper }
            else { next.helpers.append(helper) }
        }
    }
    func deleteHelper(_ id: UUID) throws {
        guard !state.runs.contains(where: { $0.helperID == id && [.queued, .running].contains($0.status) }) else {
            throw WorkspaceError.invalid("Stop this helper's active run before deleting it.")
        }
        try change { $0.helpers.removeAll { $0.id == id }; $0.routines.removeAll { $0.helperID == id } }
    }
    func save(memory: WorkspaceMemory) throws {
        try change { next in
            if let index = next.memories.firstIndex(where: { $0.id == memory.id }) { next.memories[index] = memory }
            else { next.memories.append(memory) }
        }
    }
    func deleteMemory(_ id: UUID) throws { try change { $0.memories.removeAll { $0.id == id } } }
    func save(routine: WorkspaceRoutine) throws {
        try change { next in
            if let index = next.routines.firstIndex(where: { $0.id == routine.id }) { next.routines[index] = routine }
            else { next.routines.append(routine) }
        }
    }
    func deleteRoutine(_ id: UUID) throws { try change { $0.routines.removeAll { $0.id == id } } }
    func deleteRun(_ id: UUID) throws {
        guard !state.runs.contains(where: { $0.id == id && [.queued, .running].contains($0.status) }) else {
            throw WorkspaceError.invalid("Stop the run before deleting it.")
        }
        try change { $0.runs.removeAll { $0.id == id } }
    }

    private func request(for helper: WorkspaceHelper, runID: UUID) -> WorkspaceRunRequest {
        WorkspaceRunRequest(runID: runID, helperID: helper.id, helperName: helper.name,
                            instruction: helper.instruction, scope: helper.scope,
                            memories: helper.usesMemory ? state.memories.filter(\.enabled).map(\.text) : [],
                            allowsWorkspaceWrites: helper.allowsWorkspaceWrites)
    }

    func queue(helperID: UUID, now: Date = Date()) throws -> WorkspaceRunRequest {
        guard let helper = state.helpers.first(where: { $0.id == helperID }) else { throw WorkspaceError.invalid("This helper no longer exists.") }
        guard !state.runs.contains(where: { $0.helperID == helperID && [.queued, .running].contains($0.status) }) else {
            throw WorkspaceError.invalid("This helper already has an active run.")
        }
        let run = WorkspaceRun(helperID: helper.id, helperName: helper.name, createdAt: now)
        try change { $0.runs.append(run) }
        return request(for: helper, runID: run.id)
    }

    /// Persist occurrence and queued run in the same transaction before anything is dispatched.
    func queueDueRoutines(now: Date) throws -> [WorkspaceRunRequest] {
        var requests: [WorkspaceRunRequest] = []
        try change { next in
            for index in next.routines.indices {
                let routine = next.routines[index]
                guard routine.enabled, routine.nextDue <= now,
                      routine.lastOccurrence.map({ routine.nextDue > $0 }) ?? true,
                      let helper = next.helpers.first(where: { $0.id == routine.helperID }),
                      !next.runs.contains(where: { $0.helperID == helper.id && [.queued, .running].contains($0.status) }) else { continue }
                let run = WorkspaceRun(helperID: helper.id, helperName: helper.name, routineID: routine.id,
                                       occurrence: routine.nextDue, createdAt: now)
                next.runs.append(run)
                next.routines[index].lastOccurrence = routine.nextDue
                let interval = Double(routine.intervalMinutes) * 60
                let periods = floor(now.timeIntervalSince(routine.nextDue) / interval) + 1
                next.routines[index].nextDue = routine.nextDue.addingTimeInterval(periods * interval)
                requests.append(request(for: helper, runID: run.id))
            }
        }
        return requests
    }

    func markRunning(_ id: UUID) throws {
        try change { next in
            guard let index = next.runs.firstIndex(where: { $0.id == id }), next.runs[index].status == .queued else {
                throw WorkspaceError.invalid("Only a queued run can start.")
            }
            next.runs[index].status = .running
        }
    }

    func finish(_ id: UUID, status: WorkspaceRun.Status, output: String, now: Date = Date()) throws {
        guard [.completed, .failed, .interrupted].contains(status) else { throw WorkspaceError.invalid("A terminal run status is required.") }
        try change { next in
            guard let index = next.runs.firstIndex(where: { $0.id == id }), [.queued, .running].contains(next.runs[index].status) else { return }
            next.runs[index].status = status
            next.runs[index].finishedAt = now
            next.runs[index].message = String(output.prefix(32_000))
            if status == .completed {
                next.runs[index].artifacts = [WorkspaceArtifact(name: "Answer.txt", text: String(output.prefix(32_000)))]
            }
        }
    }
}

@MainActor
final class ClickyBroWorkspaceController: ObservableObject {
    typealias Runner = @MainActor @Sendable (WorkspaceRunRequest) async throws -> String
    let store: ClickyBroWorkspaceStore
    @Published var errorMessage: String?
    // Session-only permission: relaunch never silently enables network calls.
    @Published var schedulerEnabled = false {
        didSet { if schedulerEnabled { startScheduler() } }
    }
    private let onRun: Runner
    private var tasks: [UUID: Task<Void, Never>] = [:]
    private var scheduler: Task<Void, Never>?

    init(store: ClickyBroWorkspaceStore, onRun: @escaping Runner) {
        self.store = store
        self.onRun = onRun
    }

    func start(helperID: UUID) {
        perform { dispatch(try store.queue(helperID: helperID)) }
    }
    func cancel(runID: UUID) {
        tasks[runID]?.cancel()
        tasks[runID] = nil
        perform { try store.finish(runID, status: .interrupted, output: "Stopped by you. Already completed effects cannot be undone.") }
    }
    func stopAll() {
        schedulerEnabled = false
        scheduler?.cancel()
        scheduler = nil
        for id in Array(tasks.keys) { cancel(runID: id) }
    }
    func perform(_ work: () throws -> Void) {
        do { try work(); errorMessage = nil } catch { errorMessage = error.localizedDescription }
    }
    func tick(now: Date = Date()) {
        guard schedulerEnabled else { return }
        perform { for request in try store.queueDueRoutines(now: now) { dispatch(request) } }
    }
    func startScheduler() {
        guard scheduler == nil else { return }
        scheduler = Task { [weak self] in
            while !Task.isCancelled {
                self?.tick()
                do { try await Task.sleep(for: .seconds(10)) } catch { break }
            }
        }
    }

    private func dispatch(_ request: WorkspaceRunRequest) {
        let runner = onRun
        tasks[request.runID] = Task { [weak self] in
            guard let self else { return }
            do {
                try Task.checkCancellation()
                try store.markRunning(request.runID)
                let output = try await runner(request)
                try Task.checkCancellation()
                guard !output.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                    throw WorkspaceError.invalid("The provider returned no text. This run was not completed.")
                }
                try store.finish(request.runID, status: .completed, output: output)
            } catch {
                let status: WorkspaceRun.Status = Task.isCancelled || error is CancellationError ? .interrupted : .failed
                do { try store.finish(request.runID, status: status, output: status == .interrupted ? "Run interrupted." : error.localizedDescription) }
                catch { errorMessage = error.localizedDescription }
            }
            tasks[request.runID] = nil
        }
    }
}

@MainActor
struct ClickyBroWorkspaceView: View {
    @ObservedObject var controller: ClickyBroWorkspaceController
    @ObservedObject private var store: ClickyBroWorkspaceStore
    @State private var selectedTab: ClickyBroWorkspaceTab = .helpers
    @State private var helperDraft = WorkspaceHelper(name: "", instruction: "", scope: "Answer using these instructions only; no desktop actions.")
    @State private var memoryDraft = WorkspaceMemory(text: "")
    @State private var routineDraft = WorkspaceRoutine(name: "", helperID: UUID(uuidString: "00000000-0000-0000-0000-000000000000")!, intervalMinutes: 60, nextDue: Date().addingTimeInterval(3_600))
    @State private var selectedRun: UUID?

    init(controller: ClickyBroWorkspaceController) {
        self.controller = controller
        self.store = controller.store
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("clicky-bro workspace").font(.title2.bold())
                Spacer()
                Button("Stop all") { controller.stopAll() }.pointerCursor()
            }
            Text("Helpers use your configured local agent. File writes require explicit permission below. Scope and memory notes do not grant access. Desktop actions and external integrations require separate authorization.")
                .font(.callout).foregroundStyle(.secondary)
            if let error = controller.errorMessage { Text(error).foregroundStyle(.red).textSelection(.enabled) }
            HStack(spacing: 8) {
                ForEach(ClickyBroWorkspaceTab.allCases) { tab in
                    Button {
                        selectedTab = tab
                    } label: {
                        Label(tab.title, systemImage: tab.symbol)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 7)
                            .background(
                                selectedTab == tab ? Color.accentColor.opacity(0.18) : Color.secondary.opacity(0.08),
                                in: RoundedRectangle(cornerRadius: 7)
                            )
                            .overlay {
                                RoundedRectangle(cornerRadius: 7)
                                    .stroke(selectedTab == tab ? Color.accentColor.opacity(0.6) : .clear, lineWidth: 1)
                            }
                    }
                    .buttonStyle(.plain)
                    .pointerCursor()
                    .accessibilityIdentifier("workspace.tab.\(tab.rawValue)")
                    .accessibilityValue(selectedTab == tab ? "Selected" : "")
                }
            }
            .accessibilityElement(children: .contain)

            Group {
                switch selectedTab {
                case .helpers: helpers
                case .memory: memories
                case .routines: routines
                case .history: history
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .padding(20).frame(minWidth: 820, minHeight: 560)
        .onAppear {
            if !store.state.helpers.contains(where: { $0.id == routineDraft.helperID }), let first = store.state.helpers.first { routineDraft.helperID = first.id }
            controller.startScheduler()
        }
    }

    private enum ClickyBroWorkspaceTab: String, CaseIterable, Identifiable {
        case helpers
        case memory
        case routines
        case history

        var id: String { rawValue }

        var title: String {
            switch self {
            case .helpers: "Helpers"
            case .memory: "Memory"
            case .routines: "Routines"
            case .history: "Runs & files"
            }
        }

        var symbol: String {
            switch self {
            case .helpers: "person.2"
            case .memory: "note.text"
            case .routines: "clock"
            case .history: "doc.text"
            }
        }
    }

    private var helpers: some View {
        HStack(alignment: .top, spacing: 20) {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 8) {
                    ForEach(store.state.helpers) { helper in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(helper.name).font(.headline)
                            Text(helper.scope).font(.caption).foregroundStyle(.secondary).lineLimit(2)
                            HStack(spacing: 8) {
                                Button("Edit") { helperDraft = helper }
                                    .pointerCursor()
                                    .accessibilityLabel("Edit helper \(helper.name)")
                                    .accessibilityIdentifier("workspace.helper.edit.\(helper.id.uuidString)")
                                Button("Run now") { controller.start(helperID: helper.id) }
                                    .pointerCursor()
                                    .accessibilityLabel("Run helper \(helper.name) now")
                                    .accessibilityIdentifier("workspace.helper.run.\(helper.id.uuidString)")
                                Button("Delete", role: .destructive) { controller.perform { try store.deleteHelper(helper.id) } }
                                    .pointerCursor()
                                    .accessibilityLabel("Delete helper \(helper.name)")
                                    .accessibilityIdentifier("workspace.helper.delete.\(helper.id.uuidString)")
                            }.buttonStyle(.borderless)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(10)
                        .background(Color.secondary.opacity(0.07), in: RoundedRectangle(cornerRadius: 8))
                        .accessibilityElement(children: .contain)
                    }
                }
                .padding(.vertical, 4)
            }
            .frame(minWidth: 270)
            Form {
                Text(helperDraft.name.isEmpty ? "Create a helper" : "Edit helper").font(.headline)
                TextField("Name", text: $helperDraft.name)
                    .accessibilityIdentifier("workspace.helper.name")
                Text("Instructions")
                TextEditor(text: $helperDraft.instruction)
                    .frame(minHeight: 100)
                    .accessibilityIdentifier("workspace.helper.instruction")
                Text("Scope")
                TextEditor(text: $helperDraft.scope)
                    .frame(height: 70)
                    .accessibilityIdentifier("workspace.helper.scope")
                Toggle("Include enabled memory notes", isOn: $helperDraft.usesMemory).pointerCursor()
                Toggle("Allow file writes inside the agent workspace", isOn: $helperDraft.allowsWorkspaceWrites).pointerCursor()
                Text("Off by default. This allows supported file tools only inside the configured agent workspace; it does not authorize desktop control, outside folders or external services.")
                    .font(.caption).foregroundStyle(.secondary)
                HStack {
                    Button("Save helper") { controller.perform { try store.save(helper: helperDraft) } }
                        .pointerCursor()
                        .accessibilityIdentifier("workspace.helper.save")
                    Button("New") { helperDraft = WorkspaceHelper(name: "", instruction: "", scope: "Answer only; no desktop actions.") }.pointerCursor()
                }
            }.formStyle(.grouped)
        }
    }
    private var memories: some View {
        HStack(alignment: .top, spacing: 20) {
            List(store.state.memories) { memory in
                VStack(alignment: .leading) {
                    Text(memory.text).lineLimit(4)
                    Text(memory.enabled ? "Enabled" : "Disabled").font(.caption).foregroundStyle(.secondary)
                    HStack {
                        Button("Edit") { memoryDraft = memory }
                            .pointerCursor()
                            .accessibilityIdentifier("workspace.memory.edit.\(memory.id.uuidString)")
                        Button("Delete", role: .destructive) { controller.perform { try store.deleteMemory(memory.id) } }
                            .pointerCursor()
                            .accessibilityIdentifier("workspace.memory.delete.\(memory.id.uuidString)")
                    }
                    .buttonStyle(.borderless)
                }
                .padding(.vertical, 5)
                .accessibilityElement(children: .contain)
                .accessibilityIdentifier("workspace.memory.row.\(memory.id.uuidString)")
            }
            Form {
                Text("Explicit memory notes").font(.headline)
                Text("Only helpers with memory enabled receive enabled notes. Nothing is automatically inferred or saved.")
                TextEditor(text: $memoryDraft.text).frame(minHeight: 150)
                Toggle("Enable this note", isOn: $memoryDraft.enabled).pointerCursor()
                Button("Save note") { controller.perform { try store.save(memory: memoryDraft) } }.pointerCursor()
                Button("New note") { memoryDraft = WorkspaceMemory(text: "") }.pointerCursor()
            }.formStyle(.grouped)
        }
    }
    private var routines: some View {
        HStack(alignment: .top, spacing: 20) {
            VStack(alignment: .leading) {
                Toggle("Allow scheduled model calls this session", isOn: $controller.schedulerEnabled).pointerCursor()
                Text("Runs only while clicky-bro is open. Off again after relaunch. Missed intervals are not replayed in a burst.")
                    .font(.caption).foregroundStyle(.secondary)
                List(store.state.routines) { routine in
                    VStack(alignment: .leading, spacing: 5) {
                        Text(routine.name).font(.headline)
                        Text("\(routine.enabled ? "Enabled" : "Paused") · every \(routine.intervalMinutes) min")
                        Text("Next: \(routine.nextDue.formatted())").font(.caption)
                        HStack {
                            Button("Edit") { routineDraft = routine }
                                .pointerCursor()
                                .accessibilityIdentifier("workspace.routine.edit.\(routine.id.uuidString)")
                            Button("Run now") { controller.start(helperID: routine.helperID) }
                                .pointerCursor()
                                .accessibilityIdentifier("workspace.routine.run.\(routine.id.uuidString)")
                            Button("Delete", role: .destructive) { controller.perform { try store.deleteRoutine(routine.id) } }
                                .pointerCursor()
                                .accessibilityIdentifier("workspace.routine.delete.\(routine.id.uuidString)")
                        }
                        .buttonStyle(.borderless)
                    }
                    .accessibilityElement(children: .contain)
                    .accessibilityIdentifier("workspace.routine.row.\(routine.id.uuidString)")
                }
            }
            Form {
                TextField("Routine name", text: $routineDraft.name)
                Picker("Helper", selection: $routineDraft.helperID) {
                    Text("Choose a helper").tag(UUID(uuidString: "00000000-0000-0000-0000-000000000000")!)
                    ForEach(store.state.helpers) { Text($0.name).tag($0.id) }
                }.pointerCursor()
                TextField("Interval (minutes)", value: $routineDraft.intervalMinutes, format: .number)
                DatePicker("Next run", selection: $routineDraft.nextDue).pointerCursor()
                Toggle("Enable routine", isOn: $routineDraft.enabled).pointerCursor()
                Button("Save routine") { controller.perform { try store.save(routine: routineDraft) } }.pointerCursor()
                Button("New routine") {
                    routineDraft = WorkspaceRoutine(name: "", helperID: store.state.helpers.first?.id ?? UUID(uuidString: "00000000-0000-0000-0000-000000000000")!, intervalMinutes: 60, nextDue: Date().addingTimeInterval(3_600))
                }.pointerCursor()
            }.formStyle(.grouped)
        }
    }
    private var history: some View {
        HStack(alignment: .top, spacing: 20) {
            List(selection: $selectedRun) {
                ForEach(store.state.runs.reversed()) { run in
                    VStack(alignment: .leading) {
                        Text(run.helperName).font(.headline)
                        Text("\(run.status.rawValue) · \(run.createdAt.formatted())").font(.caption)
                    }.tag(run.id)
                }
            }.frame(minWidth: 260)
            if let run = store.state.runs.first(where: { $0.id == selectedRun }) {
                ScrollView {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(run.helperName).font(.title3)
                        Text("Status: \(run.status.rawValue)")
                        if [.queued, .running].contains(run.status) {
                            Button("Stop run") { controller.cancel(runID: run.id) }.pointerCursor()
                        } else {
                            Button("Delete record", role: .destructive) { controller.perform { try store.deleteRun(run.id) } }.pointerCursor()
                        }
                        Text(run.message).textSelection(.enabled)
                        ForEach(run.artifacts) { artifact in
                            Divider()
                            Text(artifact.name).font(.headline)
                            Text(artifact.text).textSelection(.enabled)
                            Button("Copy text") {
                                NSPasteboard.general.clearContents()
                                NSPasteboard.general.setString(artifact.text, forType: .string)
                            }.pointerCursor()
                        }
                    }.frame(maxWidth: .infinity, alignment: .leading).padding()
                }
            } else { Text("Select a run to inspect its result. Outputs are saved locally as text artifacts.").foregroundStyle(.secondary).frame(maxWidth: .infinity) }
        }
    }
}
