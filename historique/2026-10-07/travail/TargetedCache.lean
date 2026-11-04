-- Workspace helper; uses the upstream hash and download implementations unchanged.
-- Hash only requested dependency closures rather than unrelated Mathlib modules.
import Cache.Cli
import Cache.Requests

open Cache Cache.Cli Cache.IO Cache.Hashing Cache.Requests

def main (args : List String) : IO Unit := CacheM.run do
  let requested ← parseArgs ("get" :: args)
  if requested.isEmpty then
    throw <| IO.userError "Provide explicit module names"
  let rootHash ← getRootHash
  let (_, memo) ← StateT.run
    (requested.toArray.mapM fun (name, path) => getHash name path)
    { rootHash := rootHash }
  IO.println s!"Targeted cache: {memo.hashMap.size} source-matched modules"
  let goodCurl ← validateCurl
  getFiles "leanprover-community/mathlib4" memo.hashMap false false goodCurl true
