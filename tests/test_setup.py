import importlib.util,unittest,tempfile,tarfile,io,hashlib
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location("setup",Path(__file__).resolve().parents[1]/"scripts/setup.py")
setup=importlib.util.module_from_spec(spec);spec.loader.exec_module(setup)
class SetupTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
 def archive(self,members):
  p=self.root/"input.tar"
  with tarfile.open(p,"w") as tar:
   for name,body,link in members:
    m=tarfile.TarInfo(name)
    if link is not None:m.type=tarfile.SYMTYPE;m.linkname=link;tar.addfile(m)
    else:m.size=len(body);m.mode=0o755;tar.addfile(m,io.BytesIO(body))
  return p
 def test_extract_preserves_executable_and_symlink(self):
  a=self.archive([("app/bin/tool",b"tool",None),("app/launcher",b"","bin/tool")]);setup.unpack(a,self.root/"out")
  self.assertEqual((self.root/"out/app/launcher").read_bytes(),b"tool")
  self.assertTrue((self.root/"out/app/bin/tool").stat().st_mode&0o100)
 def test_archive_cannot_escape_directory(self):
  a=self.archive([("../outside",b"bad",None)])
  with self.assertRaises(ValueError):setup.unpack(a,self.root/"out")
  self.assertFalse((self.root/"outside").exists())
 def test_archive_cannot_write_through_link(self):
  a=self.archive([("link",b"","../elsewhere"),("link/data",b"safe",None)])
  with self.assertRaises((ValueError,FileExistsError)):setup.unpack(a,self.root/"out")
  self.assertFalse((self.root/"elsewhere/data").exists())
 def test_verified_cache_skips_network(self):
  p=self.root/"cached";p.write_bytes(b"verified");digest=hashlib.sha256(b"verified").hexdigest()
  with patch.object(setup.urllib.request,"urlopen") as fetch:
   setup.download("https://example.invalid/asset",p,digest);fetch.assert_not_called()
 def test_bad_download_never_replaces_old_file(self):
  p=self.root/"cached";p.write_bytes(b"old")
  with patch.object(setup.urllib.request,"urlopen",return_value=io.BytesIO(b"incorrect")):
   with self.assertRaises(RuntimeError):setup.download("https://example.invalid/asset",p,"0"*64)
  self.assertEqual(p.read_bytes(),b"old");self.assertFalse((self.root/"cached.part").exists())
 def test_new_install_refuses_existing_destination(self):
  p=self.root/"existing.app";p.mkdir();(p/"personal").write_text("keep")
  with self.assertRaises(RuntimeError):setup.prepare_new(p,self.root/"cache")
  self.assertEqual((p/"personal").read_text(),"keep")
if __name__=="__main__":unittest.main()
