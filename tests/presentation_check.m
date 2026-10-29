#import <AppKit/AppKit.h>
int main(int argc, char **argv) {
 @autoreleasepool {
  if (argc != 3) return 3;
  [NSApplication sharedApplication];
  BOOL expected = strcmp(argv[2], "hidden") == 0;
  NSStatusItem *item = [NSStatusBar.systemStatusBar statusItemWithLength:NSVariableStatusItemLength];
  if ((item == nil) != expected) return 1;
  if (expected) {
   [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
   if (NSApp.activationPolicy != NSApplicationActivationPolicyAccessory) return 2;
  } else if (item) { [NSStatusBar.systemStatusBar removeStatusItem:item]; }
  puts(expected ? "Steam duplicate presentation hidden" : "Other application unchanged");
  return 0;
 }
}
