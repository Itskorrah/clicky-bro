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
