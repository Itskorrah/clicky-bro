//
//  OpenClickyUITestsLaunchTests.swift
//  OpenClickyUITests
//
//  Created by thorfinn on 3/2/26.
//

import XCTest

final class OpenClickyUITestsLaunchTests: XCTestCase {
    private var testHome: URL!
    private var appUnderTest: XCUIApplication?

    override class var runsForEachTargetApplicationUIConfiguration: Bool {
        true
    }

    override func setUpWithError() throws {
        continueAfterFailure = false
        testHome = try OpenClickyUITestSupport.makeHome()
    }

    override func tearDownWithError() throws {
        if let appUnderTest, appUnderTest.state != .notRunning {
            appUnderTest.terminate()
        }
        if let testHome {
            try? FileManager.default.removeItem(at: testHome)
        }
    }

    @MainActor
    func testLaunch() throws {
        let app = try OpenClickyUITestSupport.makeApplication(home: testHome)
        appUnderTest = app
        app.launch()

        // Insert steps here to perform after app launch but before taking a screenshot,
        // such as logging into a test account or navigating somewhere in the app

        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = "Launch Screen"
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
