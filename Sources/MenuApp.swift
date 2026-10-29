import AppKit

final class AppDelegate: NSObject, NSApplicationDelegate, NSMenuDelegate {
    var item: NSStatusItem!
    let status = NSMenuItem(title: "Windows Steam", action: nil, keyEquivalent: "")
    var busy = false
    var terminating = false
    var allowExit = false
    let work = DispatchQueue(label: "windows-steam.control")
    var wrapper: URL {
        // The helper is embedded in Wrapper.app/Contents/Resources/.
        Bundle.main.bundleURL.deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
    }
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        if let icon = NSImage(contentsOf: wrapper.appendingPathComponent("Contents/Resources/Steam.icns")) {
            NSApp.applicationIconImage = icon
        }
        let mainMenu = NSMenu(); let root = NSMenuItem(); let appMenu = NSMenu()
        let openItem = NSMenuItem(title: "Steam 창 열기", action: #selector(showSteam), keyEquivalent: "")
        openItem.target = self; appMenu.addItem(openItem); appMenu.addItem(.separator())
        let exitItem = NSMenuItem(title: "Windows Steam 종료", action: #selector(quitSteam), keyEquivalent: "q")
        exitItem.target = self; appMenu.addItem(exitItem)
        root.submenu = appMenu; mainMenu.addItem(root); NSApp.mainMenu = mainMenu
        let menu = NSMenu(); menu.delegate = self
        status.isEnabled = false; menu.addItem(status); menu.addItem(.separator())
        let show = NSMenuItem(title: "Steam 창 열기", action: #selector(showSteam), keyEquivalent: "")
        show.target = self; menu.addItem(show)
        menu.addItem(.separator())
        let quit = NSMenuItem(title: "Windows Steam 종료", action: #selector(quitSteam), keyEquivalent: "q")
        quit.target = self; menu.addItem(quit)
        item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        item.button?.image = NSImage(systemSymbolName: "gamecontroller.fill", accessibilityDescription: "Windows Steam")
        item.button?.toolTip = "Windows Steam"
        item.menu = menu // Native tracking dismisses on outside clicks, Escape and app switches.
        DistributedNotificationCenter.default().addObserver(self, selector: #selector(quitSteam),
            name: Notification.Name("local.windowssteam.menu.quit"), object: nil)
        if CommandLine.arguments.contains("--quit") { quitSteam() } else { showSteam() }
    }
    func menuWillOpen(_ menu: NSMenu) {
        if busy { return }
        work.async {
            let result = self.command("status")
            DispatchQueue.main.async {
                self.status.title = result.1.trimmingCharacters(in: .whitespacesAndNewlines) == "running"
                    ? "Windows Steam · 실행 중" : "Windows Steam · 꺼짐"
            }
        }
    }
    func command(_ action: String) -> (Int32, String) {
        let p = Process(); let output = Pipe()
        p.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        p.arguments = [Bundle.main.resourceURL!.appendingPathComponent("steam_control.py").path,
                       action, "--wrapper", wrapper.path]
        p.standardOutput = output; p.standardError = output
        do { try p.run(); let data = output.fileHandleForReading.readDataToEndOfFile(); p.waitUntilExit()
             return (p.terminationStatus, String(data: data, encoding: .utf8) ?? "") }
        catch { return (1, error.localizedDescription) }
    }
    @objc func showSteam() {
        guard !busy && !terminating else { return }
        busy = true; status.title = "Steam 창 여는 중…"
        work.async {
            let result = self.command("open")
            DispatchQueue.main.async {
                self.busy = false; self.status.title = "Windows Steam"
                if result.0 != 0 { self.error(result.1) }
            }
        }
    }
    @objc func quitSteam() { NSApp.terminate(nil) }
    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply {
        if allowExit { return .terminateNow }
        if terminating { return .terminateLater }
        terminating = true; status.title = "Windows Steam 종료 중…"
        // Serialized with any in-flight launch, so a late launch cannot restart after quit.
        work.async {
            let result = self.command("quit")
            DispatchQueue.main.async {
                self.terminating = false
                if result.0 == 0 { self.allowExit = true; NSApp.reply(toApplicationShouldTerminate: true) }
                else { self.status.title = "종료 실패"; NSApp.reply(toApplicationShouldTerminate: false); self.error(result.1) }
            }
        }
        return .terminateLater
    }
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { false }
    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        showSteam(); return true
    }
    func error(_ message: String) {
        NSApp.activate(ignoringOtherApps: true)
        let alert = NSAlert(); alert.messageText = "Windows Steam"; alert.informativeText = message
        alert.runModal()
    }
}
if CommandLine.arguments.contains("--quit"),
   NSRunningApplication.runningApplications(withBundleIdentifier: "local.windowssteam.menu").contains(where: { $0.processIdentifier != ProcessInfo.processInfo.processIdentifier }) {
    DistributedNotificationCenter.default().postNotificationName(Notification.Name("local.windowssteam.menu.quit"), object: nil, userInfo: nil, deliverImmediately: true)
    exit(0)
}
let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
