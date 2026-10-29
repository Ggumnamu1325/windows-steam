import AppKit
let helper = Bundle.main.resourceURL!.appendingPathComponent("Windows Steam Menu.app")
let config = NSWorkspace.OpenConfiguration()
config.activates = false
NSWorkspace.shared.openApplication(at: helper, configuration: config) { _, error in
    if let error = error { fputs("Windows Steam: \(error.localizedDescription)\n", stderr); exit(1) }
    exit(0)
}
RunLoop.main.run()
