import importlib.util,unittest,subprocess
from pathlib import Path
spec=importlib.util.spec_from_file_location("presentation",Path(__file__).resolve().parents[1]/"scripts/presentation_config.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class PresentationConfigTests(unittest.TestCase):
 def test_custom_commands_reach_wine_with_space_and_quote(self):
  path="/Applications/A User's Steam.app/Contents/Resources/Control.dylib"
  result=mod.configure({},path)
  command=result['CLI Custom Commands']+' printf "%s" "$DYLD_INSERT_LIBRARIES"'
  self.assertEqual(subprocess.check_output(['/bin/sh','-c',command],text=True),path)
 def test_existing_commands_and_comments_are_preserved(self):
  original='export USER_OPTION=kept; # user comment'
  result=mod.configure({'CLI Custom Commands':original},'/safe/control.dylib')
  command=result['CLI Custom Commands']+' printf "%s:%s" "$USER_OPTION" "$WINDOWS_STEAM_PRESENTATION"'
  self.assertEqual(subprocess.check_output(['/bin/sh','-c',command],text=True),'kept:1')
 def test_repeated_install_is_idempotent(self):
  first=mod.configure({'CLI Custom Commands':'export ORIGINAL=1;'},'/safe/control.dylib')
  self.assertEqual(mod.configure(first,'/safe/control.dylib'),first)
  self.assertTrue(first['LSUIElement'])
if __name__=='__main__':unittest.main()
