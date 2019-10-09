from pathlib import Path
import yamlIo

ledger = yamlIo.readOld(Path("data/finances"))
yamlIo.write(ledger, Path("data/financesNew"))
