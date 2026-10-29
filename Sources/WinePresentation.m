// Presentation changes apply only to the selected wrapper's Steam client processes.
#import <AppKit/AppKit.h>
#import <objc/runtime.h>

static BOOL isSteamClient(void) {
    NSSet *names = [NSSet setWithArray:@[@"sikarugir", @"steam.exe", @"steamwebhelper.exe"]];
    for (NSString *argument in NSProcessInfo.processInfo.arguments) {
        NSString *name = [[[argument stringByReplacingOccurrencesOfString:@"\\" withString:@"/"] lastPathComponent] lowercaseString];
        if ([names containsObject:name]) return YES;
    }
    return [names containsObject:NSProcessInfo.processInfo.processName.lowercaseString];
}

@implementation NSApplication (WindowsSteamPresentation)
- (BOOL)ws_setActivationPolicy:(NSApplicationActivationPolicy)policy {
    return [self ws_setActivationPolicy:NSApplicationActivationPolicyAccessory];
}
@end
@implementation NSStatusBar (WindowsSteamPresentation)
- (NSStatusItem *)ws_statusItemWithLength:(CGFloat)length { return nil; }
@end

__attribute__((constructor)) static void configurePresentation(void) {
    @autoreleasepool {
        if (![[NSProcessInfo.processInfo.environment objectForKey:@"WINDOWS_STEAM_PRESENTATION"] isEqualToString:@"1"] || !isSteamClient()) return;
        method_exchangeImplementations(class_getInstanceMethod(NSApplication.class, @selector(setActivationPolicy:)),
                                       class_getInstanceMethod(NSApplication.class, @selector(ws_setActivationPolicy:)));
        method_exchangeImplementations(class_getInstanceMethod(NSStatusBar.class, @selector(statusItemWithLength:)),
                                       class_getInstanceMethod(NSStatusBar.class, @selector(ws_statusItemWithLength:)));
        [NSNotificationCenter.defaultCenter addObserverForName:NSApplicationDidFinishLaunchingNotification object:nil queue:NSOperationQueue.mainQueue usingBlock:^(NSNotification *note) {
            [NSApp setActivationPolicy:NSApplicationActivationPolicyAccessory];
        }];
    }
}
