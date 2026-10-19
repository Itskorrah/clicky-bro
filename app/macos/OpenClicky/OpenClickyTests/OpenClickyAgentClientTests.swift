import Foundation
import Testing
@testable import OpenClicky

@MainActor
struct OpenClickyAgentClientTests {
    @Test func anOldCancelledProcessCannotClearTheNewProcessHandle() async throws {
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent("clicky-agent-process-\(UUID().uuidString)", isDirectory: true)
        let state = directory.appendingPathComponent("state", isDirectory: true)
        try FileManager.default.createDirectory(at: state, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }

        let script = directory.appendingPathComponent("fake-cli.sh")
        let scriptText = #"""
        #!/bin/sh
        set -eu
        case "$2" in
          old)
            : > "$FAKE_STATE/old-started"
            trap '' INT
            trap ': > "$FAKE_STATE/old-exited"; exit 0' TERM
            while [ ! -e "$FAKE_STATE/release-old" ]; do /bin/sleep 0.02; done
            : > "$FAKE_STATE/old-exited"
            ;;
          new)
            : > "$FAKE_STATE/new-started"
            trap ': > "$FAKE_STATE/new-stopped"; exit 0' INT
            trap ': > "$FAKE_STATE/new-terminated"; exit 0' TERM
            while [ ! -e "$FAKE_STATE/release-new" ]; do /bin/sleep 0.02; done
            : > "$FAKE_STATE/new-released"
            ;;
        esac
        """#
        try scriptText.write(to: script, atomically: true, encoding: .utf8)
        try FileManager.default.setAttributes([.posixPermissions: 0o700], ofItemAtPath: script.path)

        let client = OpenClickyAgentClient(
            cliCommand: ["/bin/sh", script.path],
            processEnvironment: ["PATH": "/bin:/usr/bin", "FAKE_STATE": state.path],
            workspacePath: directory.path
        )

        let oldRun = Task { await client.classifyLane(for: "old") }
        let oldStarted = await waitForMarker("old-started", in: state, timeout: 1)
        client.cancel()
        let newRun = Task { await client.classifyLane(for: "new") }
        let newStarted = await waitForMarker("new-started", in: state, timeout: 1)

        // The old process ignores SIGINT and is terminated by the client's two-second fallback.
        let oldExited = await waitForMarker("old-exited", in: state, timeout: 4)
        if !oldExited { try writeMarker("release-old", in: state) }
        let oldLane = await oldRun.value

        // If the old termination handler cleared runningProcess unconditionally, this Stop is a
        // no-op and the new process stays alive until the test's release marker is written.
        client.cancel()
        let newStopped = await waitForMarker("new-stopped", in: state, timeout: 1)
        if !newStopped { try writeMarker("release-new", in: state) }
        let newLane = await newRun.value

        #expect(oldStarted)
        #expect(newStarted)
        #expect(oldExited)
        #expect(oldLane == "agent")
        #expect(newStopped)
        #expect(newLane == "agent")
    }

    private func waitForMarker(_ name: String, in directory: URL, timeout: TimeInterval) async -> Bool {
        let marker = directory.appendingPathComponent(name)
        let deadline = Date().addingTimeInterval(timeout)
        while !FileManager.default.fileExists(atPath: marker.path), Date() < deadline {
            try? await Task.sleep(nanoseconds: 20_000_000)
        }
        return FileManager.default.fileExists(atPath: marker.path)
    }

    private func writeMarker(_ name: String, in directory: URL) throws {
        try Data().write(to: directory.appendingPathComponent(name))
    }
}
