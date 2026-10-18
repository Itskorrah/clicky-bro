//
//  OpenClickyUITests.swift
//  OpenClickyUITests
//
//  Created by thorfinn on 3/2/26.
//

import XCTest

enum OpenClickyUITestSupport {
    static func makeHome() throws -> URL {
        let home = FileManager.default.temporaryDirectory
            .appendingPathComponent("clicky-bro-ui-\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: home, withIntermediateDirectories: true)
        return home
    }

    static func makeApplication(home: URL) throws -> XCUIApplication {
        let appData = home.appendingPathComponent(".clicky-bro", isDirectory: true)
        let workspace = home.appendingPathComponent("workspace", isDirectory: true)
        let skills = home.appendingPathComponent("skills", isDirectory: true)
        for directory in [appData, workspace, skills] {
            try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        }

        let app = XCUIApplication()
        app.launchEnvironment["HOME"] = home.path
        app.launchEnvironment["CLICKY_BRO_HOME"] = appData.path
        app.launchEnvironment["CLICKY_BRO_WORKSPACE"] = workspace.path
        app.launchEnvironment["CLICKY_BRO_USER_SKILLS_DIR"] = skills.path
        app.launchEnvironment["CLICKY_BRO_GEMINI_KEY_FILE"] = home.appendingPathComponent("missing-gemini-key.json").path
        app.launchEnvironment["CLICKY_BRO_SHELL_CLI"] = "/usr/bin/false"
        app.launchEnvironment["BACKEND_URL"] = "http://127.0.0.1:1"
        for name in [
            "CLICKY_BRO_TOKEN", "CLICKY_BRO_OPENAI_KEY", "CLICKY_BRO_ANTHROPIC_KEY",
            "CLICKY_BRO_GEMINI_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
            "GOOGLE_API_KEY", "GROQ_API_KEY", "MISTRAL_API_KEY", "XAI_API_KEY",
            "COMPOSIO_API_KEY", "COMPOSIO_MCP_URL",
        ] {
            app.launchEnvironment[name] = ""
        }
        return app
    }
}

final class OpenClickyUITests: XCTestCase {
    private var testHome: URL!
    private var appUnderTest: XCUIApplication?

    override func setUpWithError() throws {
        // Put setup code here. This method is called before the invocation of each test method in the class.

        // In UI tests it is usually best to stop immediately when a failure occurs.
        continueAfterFailure = false

        // In UI tests it’s important to set the initial state - such as interface orientation - required for your tests before they run. The setUp method is a good place to do this.
        testHome = try OpenClickyUITestSupport.makeHome()
    }

    override func tearDownWithError() throws {
        // Put teardown code here. This method is called after the invocation of each test method in the class.
        if let appUnderTest, appUnderTest.state != .notRunning {
            appUnderTest.terminate()
        }
        if let testHome {
            try? FileManager.default.removeItem(at: testHome)
        }
    }

    private func makeApplication() throws -> XCUIApplication {
        let app = try OpenClickyUITestSupport.makeApplication(home: testHome)
        appUnderTest = app
        return app
    }

    @MainActor
    func testExample() throws {
        // UI tests must launch the application that they test.
        let app = try makeApplication()
        app.launch()

        // Use XCTAssert and related functions to verify your tests produce the correct results.
    }

    @MainActor
    func testWorkspaceSectionsAreSeparateAccessibleControls() throws {
        let app = try makeApplication()
        app.launch()

        let helpers = app.buttons["workspace.tab.helpers"]
        let memory = app.buttons["workspace.tab.memory"]
        let routines = app.buttons["workspace.tab.routines"]
        let history = app.buttons["workspace.tab.history"]

        XCTAssertTrue(helpers.waitForExistence(timeout: 10))
        XCTAssertTrue(memory.exists)
        XCTAssertTrue(routines.exists)
        XCTAssertTrue(history.exists)

        memory.tap()
        XCTAssertTrue(app.staticTexts["Explicit memory notes"].waitForExistence(timeout: 5))
        routines.tap()
        XCTAssertTrue(app.textFields["Routine name"].waitForExistence(timeout: 5))
        history.tap()
        XCTAssertTrue(app.staticTexts["Select a run to inspect its result. Outputs are saved locally as text artifacts."].waitForExistence(timeout: 5))
        helpers.tap()
        XCTAssertTrue(app.staticTexts["Create a helper"].waitForExistence(timeout: 5))
    }

    @MainActor
    func testHelperRowActionsAreSeparateAccessibleButtons() throws {
        let app = try makeApplication()
        app.launch()

        let name = "AX fixture \(UUID().uuidString)"
        let nameField = app.textFields["workspace.helper.name"]
        XCTAssertTrue(nameField.waitForExistence(timeout: 10))
        nameField.tap()
        nameField.typeText(name)

        let instructions = app.textViews["workspace.helper.instruction"]
        XCTAssertTrue(instructions.exists)
        instructions.tap()
        instructions.typeText("Return a brief text response.")

        let scope = app.textViews["workspace.helper.scope"]
        XCTAssertTrue(scope.exists)
        scope.tap()
        scope.typeText("Text only. Do not write files or use desktop tools.")

        app.buttons["workspace.helper.save"].tap()

        let edit = app.buttons.matching(NSPredicate(format: "label == %@", "Edit helper \(name)")).firstMatch
        let run = app.buttons.matching(NSPredicate(format: "label == %@", "Run helper \(name) now")).firstMatch
        let delete = app.buttons.matching(NSPredicate(format: "label == %@", "Delete helper \(name)")).firstMatch
        XCTAssertTrue(edit.waitForExistence(timeout: 5))
        XCTAssertTrue(run.exists)
        XCTAssertTrue(delete.exists)
        XCTAssertTrue(edit.isHittable)
        XCTAssertTrue(run.isHittable)
        XCTAssertTrue(delete.isHittable)
    }

    @MainActor
    func testLaunchPerformance() throws {
        // This measures how long it takes to launch your application.
        let app = try makeApplication()
        measure(metrics: [XCTApplicationLaunchMetric()]) {
            app.launch()
        }
    }
}
