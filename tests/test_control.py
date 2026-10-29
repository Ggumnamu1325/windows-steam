import importlib.util, tempfile, unittest, subprocess, os
from pathlib import Path
from unittest.mock import patch, Mock
spec=importlib.util.spec_from_file_location("control",Path(__file__).resolve().parents[1]/"scripts/steam_control.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class LifecycleTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.c=mod.Controller(Path(self.tmp.name)/"Example.app")
 def test_every_command_is_prefix_scoped(self):
  with patch.object(mod.subprocess,"run",return_value=Mock(returncode=0)) as run:
   self.assertTrue(self.c.wait_stopped(1));args=run.call_args
   self.assertEqual(args.kwargs["env"]["WINEPREFIX"],str(self.c.prefix))
   self.assertEqual(args.args[0],[str(self.c.bin/"wineserver"),"-w"])
 def test_graceful_quit_never_kills_healthy_session(self):
  with patch.object(self.c,"validate"),patch.object(self.c,"running",return_value=True),patch.object(self.c,"run") as run,patch.object(self.c,"wait_stopped",return_value=True):
   self.c.quit();self.assertEqual(run.call_count,1);self.assertEqual(run.call_args.args[1][-1],"-shutdown")
 def test_hung_quit_kills_only_own_wineserver(self):
  with patch.object(self.c,"validate"),patch.object(self.c,"running",return_value=True),patch.object(self.c,"run") as run,patch.object(self.c,"wait_stopped",side_effect=[False,True]):
   self.c.quit();self.assertEqual(run.call_args.args[0],self.c.bin/"wineserver");self.assertEqual(run.call_args.args[1],["-k"])
 def test_failed_exit_is_reported(self):
  with patch.object(self.c,"validate"),patch.object(self.c,"running",return_value=True),patch.object(self.c,"run"),patch.object(self.c,"wait_stopped",return_value=False):
   with self.assertRaises(RuntimeError):self.c.quit()
 def test_open_running_instance_does_not_launch_duplicate(self):
  with patch.object(self.c,"validate"),patch.object(self.c,"running",return_value=True),patch.object(self.c,"run") as run,patch.object(mod.subprocess,"Popen") as spawn:
   self.c.open();spawn.assert_not_called();self.assertIn("steam://open/games",run.call_args.args[1])
 def test_live_prefix_never_removes_launch_lock(self):
  with patch.object(self.c,"running",return_value=True),patch.object(mod.Path,"unlink") as unlink:
   self.c.clear_stale_lock();unlink.assert_not_called()
if __name__=="__main__":unittest.main()
