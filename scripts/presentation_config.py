"""Build the wrapper launch configuration without discarding user custom commands."""
import re
import shlex

def configure(info, library):
    updated = dict(info)
    original = info.get('WindowsSteamOriginalCLI')
    if original is None:
        original = re.sub(r'# windows-steam-presentation.*?# end-windows-steam-presentation\n?', '',
                          info.get('CLI Custom Commands', ''), flags=re.S).strip()
    updated['WindowsSteamOriginalCLI'] = original
    # Do not end with a comment: the wrapper appends its Wine command on this line.
    commands = 'export WINDOWS_STEAM_PRESENTATION=1; export DYLD_INSERT_LIBRARIES=' + shlex.quote(str(library)) + ';'
    updated['CLI Custom Commands'] = (original + '\n' if original else '') + commands
    updated['CFBundleExecutable'] = 'WindowsSteamLauncher'
    updated['LSUIElement'] = True
    updated['Program Flags'] = '-language koreana steam://open/games'
    return updated
