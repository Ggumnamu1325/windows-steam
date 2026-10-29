// Presentation changes apply only to the selected wrapper's Steam client processes.
#import <AppKit/AppKit.h>
#import <objc/runtime.h>
#import <crt_externs.h>

static BOOL isSteamClient(void) {
    NSSet *names = [NSSet setWithArray:@[@"sikarugir", @"steam.exe", @"steamwebhelper.exe", @"explorer.exe"]];
    // Wine updates argv after dylib constructors; Foundation may cache the old arguments.
    char **arguments = *_NSGetArgv();
    for (int i = 0; i < *_NSGetArgc(); i++) {
        if (!arguments[i]) continue;
        NSString *argument = [NSString stringWithUTF8String:arguments[i]];
        NSString *name = [[[argument stringByReplacingOccurrencesOfString:@"\\" withString:@"/"] lastPathComponent] lowercaseString];
        if ([names containsObject:name]) return YES;
    }
    return [names containsObject:NSProcessInfo.processInfo.processName.lowercaseString];
}

@implementation NSApplication (WindowsSteamPresentation)
- (BOOL)ws_setActivationPolicy:(NSApplicationActivationPolicy)policy {
    return [self ws_setActivationPolicy:isSteamClient() ? NSApplicationActivationPolicyAccessory : policy];
}
@end
@implementation NSStatusBar (WindowsSteamPresentation)
- (NSStatusItem *)ws_statusItemWithLength:(CGFloat)length {
    return isSteamClient() ? nil : [self ws_statusItemWithLength:length];
}
@end

__attribute__((constructor)) static void configurePresentation(void) {
    @autoreleasepool {
        if (![[NSProcessInfo.processInfo.environment objectForKey:@"WINDOWS_STEAM_PRESENTATION"] isEqualToString:@"1"]) return;
        method_exchangeImplementations(class_getInstanceMethod(NSApplication.class, @selector(setActivationPolicy:)),
                                       class_getInstanceMethod(NSApplication.class, @selector(ws_setActivationPolicy:)));
        method_exchangeImplementations(class_getInstanceMethod(NSStatusBar.class, @selector(statusItemWithLength:)),
                                       class_getInstanceMethod(NSStatusBar.class, @selector(ws_statusItemWithLength:)));
        [NSNotificationCenter.defaultCenter addObserverForName:NSApplicationDidFinishLaunchingNotification object:nil queue:NSOperationQueue.mainQueue usingBlock:^(NSNotification *note) {
            if (isSteamClient()) [NSApp setActivationPolicy:NSApplicationActivationPolicyAccessory];
        }];
    }
}
