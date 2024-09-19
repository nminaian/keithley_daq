<#.SYNOPSIS
Initialize repository.#>

. scripts/Initialize-Shell.ps1

git init

# ? Modify GitHub repo later on only if there were not already commits in this repo
try { git rev-parse HEAD }
catch [System.Management.Automation.NativeCommandExitException] { $Fresh = $true }

git add .
try { git commit --no-verify -m 'Prepare template using blakeNaccarato/copier-python' }
catch [System.Management.Automation.NativeCommandExitException] { $AlreadyTemplated = $true }

git submodule add --force --name 'typings' 'https://github.com/microsoft/python-type-stubs.git' 'typings'
git add .
try { git commit --no-verify -m 'Add template and type stub submodules' }
catch [System.Management.Automation.NativeCommandExitException] { $HadSubmodules = $true }

. scripts/Sync-Env.ps1

git add .
try { git commit --no-verify -m 'Lock' }
catch [System.Management.Automation.NativeCommandExitException] { $AlreadyLocked = $true }

# ? Modify GitHub repo if there were not already commits in this repo
if ($Fresh) {
    if (!(git remote)) {
        git remote add origin 'https://github.com/nminaian/keithley_daq.git'
        git branch --move --force main
    }
    gh repo edit --description (Get-Content '.copier-answers.yml' | Find-Pattern '^project_description:\s(.+)$')
    gh repo edit --homepage 'https://nminaian.github.io/keithley_daq/'
}

git push --set-upstream origin main
