$exclude = @("venv", "bot_web.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "bot_web.zip" -Force