//
//  RealtimeAudioEngineConcurrencyTests.swift
//  OpenClickyTests
//
//  `RealtimeAudioEngine` hands its microphone tap to AVAudioEngine, which calls it on the CoreAudio
//  render thread — a real thread, not the serial `queue` the rest of the class is synchronised on.
//  These tests use synthetic buffers and a real converter snapshot on a paced background thread
//  while the control queue clears/replaces it. They do not start an audio graph or microphone.
//
//  They are written to be run under the Thread Sanitizer, which is where the failure is visible:
//
//      xcodebuild test -project OpenClicky.xcodeproj -scheme OpenClicky \
//        -destination 'platform=macOS' -enableThreadSanitizer YES \
//        -only-testing:OpenClickyTests/RealtimeAudioEngineConcurrencyTests
//
//  Ordinary runs assert real frames were converted, late buffers are refused after release,
//  and renderer cleanup is bounded. TSan is a separate verification requirement.
//

import AVFoundation
import Foundation
import Testing
@testable import OpenClicky

struct RealtimeAudioEngineConcurrencyTests {

    /// A 10 ms mono float buffer, the shape an input tap actually delivers.
    private static func makeInputBuffer(sampleRate: Double = 48_000) -> AVAudioPCMBuffer {
        let format = AVAudioFormat(standardFormatWithSampleRate: sampleRate, channels: 1)!
        let frameCount = AVAudioFrameCount(sampleRate / 100)
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: frameCount)!
        buffer.frameLength = frameCount
        let channel = buffer.floatChannelData![0]
        for index in 0..<Int(frameCount) {
            channel[index] = sin(Float(index) * 0.05) * 0.25
        }
        return buffer
    }

    /// A synthetic renderer feeds the same converter snapshot the real tap uses, at 10 ms
    /// cadence, while stop/release clears it. No microphone, hardware graph or TCC grant.
    /// TSan is required to establish race freedom; ordinary runs check real conversion,
    /// bounded cleanup and refusal of late buffers after release.
    @Test(.timeLimit(.minutes(1)))
    func deliveringBuffersWhileTheGraphIsTornDownIsRaceFree() async throws {
        let engine = RealtimeAudioEngine()
        let delivered = Counter()
        engine.setCallbacks(onMicrophoneFrame: { data, _ in
            if !data.isEmpty { delivered.increment() }
        }, onPlaybackActiveChanged: { _ in })
        let buffer = Self.makeInputBuffer()
        #expect(await engine.installSyntheticCaptureForTesting(inputFormat: buffer.format))
        let keepDelivering = Flag(true)
        let renderer = Self.startRenderer(engine: engine, buffer: buffer, keepDelivering: keepDelivering)
        defer { keepDelivering.value = false }
        #expect(await Self.waitForDelivery(delivered))

        for _ in 0..<200 {
            try Task.checkCancellation()
            engine.stop()
            engine.pause()
            await engine.releaseNow()
            #expect(await engine.installSyntheticCaptureForTesting(inputFormat: buffer.format))
            try await Task.sleep(for: .milliseconds(2))
        }
        keepDelivering.value = false
        #expect(await Self.joinRenderer(renderer))
        #expect(delivered.value >= 2)
        engine.stop()
        await engine.releaseNow()
        let before = delivered.value
        engine.handleMicrophoneBuffer(buffer)
        #expect(delivered.value == before)
    }

    @Test(.timeLimit(.minutes(1)))
    func readingStatisticsWhileBuffersArriveIsRaceFree() async throws {
        let engine = RealtimeAudioEngine()
        let delivered = Counter()
        engine.setCallbacks(onMicrophoneFrame: { data, _ in
            if !data.isEmpty { delivered.increment() }
        }, onPlaybackActiveChanged: { _ in })
        let buffer = Self.makeInputBuffer()
        #expect(await engine.installSyntheticCaptureForTesting(inputFormat: buffer.format))
        let keepDelivering = Flag(true)
        let renderer = Self.startRenderer(engine: engine, buffer: buffer, keepDelivering: keepDelivering)
        defer { keepDelivering.value = false }
        #expect(await Self.waitForDelivery(delivered))
        for _ in 0..<100 {
            try Task.checkCancellation()
            _ = await engine.debugSummary()
            try await Task.sleep(for: .milliseconds(2))
        }
        keepDelivering.value = false
        #expect(await Self.joinRenderer(renderer))
        #expect(delivered.value >= 2)
        engine.stop()
        await engine.releaseNow()
    }

    @Test func inactiveCaptureNeverQueuesTapStatistics() async {
        let engine = RealtimeAudioEngine()
        let before = await engine.debugSummary()
        let buffer = Self.makeInputBuffer()
        for _ in 0..<10_000 { engine.handleMicrophoneBuffer(buffer) }
        #expect(await engine.debugSummary() == before)
    }

    private static func startRenderer(engine: RealtimeAudioEngine, buffer: AVAudioPCMBuffer, keepDelivering: Flag) -> Thread {
        let renderer = Thread {
            // Even a failed/cancelled test cannot leave an immortal render thread behind.
            let deadline = Date(timeIntervalSinceNow: 10)
            while keepDelivering.value && Date() < deadline {
                engine.handleMicrophoneBuffer(buffer)
                Thread.sleep(forTimeInterval: 0.01)
            }
        }
        renderer.stackSize = 512 * 1024
        renderer.start()
        return renderer
    }

    private static func waitForDelivery(_ counter: Counter) async -> Bool {
        let deadline = Date(timeIntervalSinceNow: 2)
        while counter.value == 0 && Date() < deadline {
            try? await Task.sleep(for: .milliseconds(5))
        }
        return counter.value > 0
    }

    private static func joinRenderer(_ renderer: Thread) async -> Bool {
        let deadline = Date(timeIntervalSinceNow: 3)
        while !renderer.isFinished && Date() < deadline {
            try? await Task.sleep(for: .milliseconds(5))
        }
        return renderer.isFinished
    }

}

/// A lock-guarded flag, so the test's own stop signal is not itself the race TSan reports.
private final class Flag: @unchecked Sendable {
    private let lock = NSLock()
    private var flag: Bool

    init(_ flag: Bool) { self.flag = flag }

    var value: Bool {
        get {
            lock.lock()
            defer { lock.unlock() }
            return flag
        }
        set {
            lock.lock()
            flag = newValue
            lock.unlock()
        }
    }
}

/// A lock-guarded counter, so the test's own bookkeeping is not itself the race TSan reports.
private final class Counter: @unchecked Sendable {
    private let lock = NSLock()
    private var count = 0

    func increment() {
        lock.lock()
        count += 1
        lock.unlock()
    }

    var value: Int {
        lock.lock()
        defer { lock.unlock() }
        return count
    }
}
