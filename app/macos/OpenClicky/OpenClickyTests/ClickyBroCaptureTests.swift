import Foundation
import CoreGraphics
import Testing
@testable import OpenClicky

struct ClickyBroCaptureTests {
    @Test func selectedWindowGeometryIncludesPositionAndFlipsGlobalY() {
        let input = CGRect(x: -500, y: 120, width: 900, height: 600)
        let frame = CompanionScreenCaptureUtility.appKitFrame(for: input, primaryMaxY: 982)
        #expect(frame == CGRect(x: -500, y: 262, width: 900, height: 600))
    }
    @Test func selectedWindowAbovePrimaryKeepsNegativeDesktopCoordinates() {
        let input = CGRect(x: 200, y: -1000, width: 800, height: 500)
        let frame = CompanionScreenCaptureUtility.appKitFrame(for: input, primaryMaxY: 982)
        #expect(frame == CGRect(x: 200, y: 1482, width: 800, height: 500))
    }
    @Test func selectedWindowIdentityRequiresBothWindowAndOwningProcess() {
        let selected = CompanionWindowIdentity(windowID: 41, processID: 700)
        #expect(CompanionScreenCaptureUtility.matchesSelectedWindow(selected, windowID: 41, processID: 700))
        #expect(!CompanionScreenCaptureUtility.matchesSelectedWindow(selected, windowID: 42, processID: 700))
        #expect(!CompanionScreenCaptureUtility.matchesSelectedWindow(selected, windowID: 41, processID: 701))
        #expect(!CompanionScreenCaptureUtility.matchesSelectedWindow(nil, windowID: 41, processID: 700))
    }
    @Test func movedWindowWithUnchangedSizeIsNotTreatedAsSameCapture() {
        let before = CGRect(x: 20, y: -100, width: 800, height: 600)
        let moved = CGRect(x: 21, y: -100, width: 800, height: 600)
        let resized = CGRect(x: 20, y: -100, width: 801, height: 600)
        let infiniteOrigin = CGRect(x: .infinity, y: -100, width: 800, height: 600)
        let infiniteExtent = CGRect(x: 20, y: -100, width: .infinity, height: 600)
        #expect(CompanionScreenCaptureUtility.hasStableWindowFrame(before: before, after: before))
        #expect(!CompanionScreenCaptureUtility.hasStableWindowFrame(before: before, after: moved))
        #expect(!CompanionScreenCaptureUtility.hasStableWindowFrame(before: before, after: resized))
        #expect(!CompanionScreenCaptureUtility.hasStableWindowFrame(before: .zero, after: .zero))
        #expect(!CompanionScreenCaptureUtility.hasStableWindowFrame(before: infiniteOrigin, after: infiniteOrigin))
        #expect(!CompanionScreenCaptureUtility.hasStableWindowFrame(before: infiniteExtent, after: infiniteExtent))
    }

    @Test func captureSizingRejectsNonFiniteGeometryBeforeIntegerConversion() {
        let valid = CGRect(x: 0, y: 0, width: 1600, height: 900)
        let infiniteOrigin = CGRect(x: .infinity, y: 0, width: 1600, height: 900)
        let infiniteExtent = CGRect(x: 0, y: 0, width: .infinity, height: 900)
        #expect(CompanionScreenCaptureUtility.captureDimensions(for: valid)?.width == 1280)
        #expect(CompanionScreenCaptureUtility.captureDimensions(for: valid)?.height == 720)
        #expect(CompanionScreenCaptureUtility.captureDimensions(for: infiniteOrigin)?.width == nil)
        #expect(CompanionScreenCaptureUtility.captureDimensions(for: infiniteExtent)?.height == nil)
    }

    @Test func captureDiagnosisSeparatesPermissionFromDeliveredFrame() {
        let stale = CompanionCaptureDiagnosis(permissionReported: true, hadSelectedWindow: true,
            frameCaptured: false, detail: "capture denied")
        let working = CompanionCaptureDiagnosis(permissionReported: false, hadSelectedWindow: true,
            frameCaptured: true, detail: "frame available")
        #expect(stale.summary.contains("No usable local frame"))
        #expect(working.summary.contains("Local frame captured"))
        #expect(stale.summary.contains("macOS reports Screen Recording allowed"))
    }

    @Test func privateKeyReaderRejectsSymlinksAndPublicPermissions() throws {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }
        let file = directory.appendingPathComponent("key.json")
        try Data("{\"api_key\":\"test-placeholder\"}".utf8).write(to: file)
        try FileManager.default.setAttributes([.posixPermissions: 0o600], ofItemAtPath: file.path)
        #expect(ClickyBroPaths.readPrivateKey(at: file) == "test-placeholder")
        let link = directory.appendingPathComponent("link.json")
        try FileManager.default.createSymbolicLink(at: link, withDestinationURL: file)
        #expect(ClickyBroPaths.readPrivateKey(at: link) == nil)
        try FileManager.default.setAttributes([.posixPermissions: 0o644], ofItemAtPath: file.path)
        #expect(ClickyBroPaths.readPrivateKey(at: file) == nil)
    }
}
