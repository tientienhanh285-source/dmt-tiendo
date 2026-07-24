
$word = New-Object -ComObject Word.Application -ErrorAction SilentlyContinue
if ($word -eq $null) {
    Write-Host "MS Word is NOT installed or COM is unavailable."
    exit 1
}
$word.Visible = $false
$files = Get-ChildItem "INPUT\DMT Group\*.doc"
foreach ($f in $files) {
    if ($f.Extension -eq ".doc") {
        $doc = $word.Documents.Open($f.FullName)
        $docxName = $f.FullName + "x"
        $doc.SaveAs2($docxName, 16) # wdFormatXMLDocument
        $doc.Close()
        Write-Host "Converted: $($f.Name) to $($f.Name)x"
    }
}
$word.Quit()
