param(
    [string]$Tau2Source = $env:NIL_CCEA_TAU2_SRC,
    [string]$CondaEnv = "nil_ccea_tau2_py312"
)

$ErrorActionPreference = "Stop"
if (-not $Tau2Source -or -not (Test-Path (Join-Path $Tau2Source "src\tau2"))) {
    throw "请通过 -Tau2Source 或 NIL_CCEA_TAU2_SRC 指定 tau2-bench v1.0.1 源码目录"
}

$repo = (Get-Location).Path
$stub = Join-Path $repo "tests\support\litellm_stub"
$env:PYTHONPATH = "$stub;$Tau2Source\src;$repo\src"
conda run -n $CondaEnv python -m unittest discover -s tests -v
