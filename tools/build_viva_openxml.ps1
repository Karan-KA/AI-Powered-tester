$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$out = Join-Path $root "docs\AI-Web-Test-Automation-Viva.pptx"
$work = Join-Path $root "outputs\manual-viva-presentation\openxml-package"

@(
  $work,
  "$work\_rels",
  "$work\docProps",
  "$work\ppt",
  "$work\ppt\_rels",
  "$work\ppt\slides",
  "$work\ppt\slides\_rels",
  "$work\ppt\theme",
  "$work\ppt\slideMasters",
  "$work\ppt\slideMasters\_rels",
  "$work\ppt\slideLayouts",
  "$work\ppt\slideLayouts\_rels"
) | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }

$slideW = 12192000
$slideH = 6858000
$id = 100

function Emu($inch) { [int64]($inch * 914400) }
function Esc($text) { [System.Security.SecurityElement]::Escape([string]$text) }
function WriteText($path, $text) {
  if ([System.IO.File]::Exists($path)) {
    [System.IO.File]::SetAttributes($path, [System.IO.FileAttributes]::Normal)
  }
  [System.IO.File]::WriteAllText($path, $text, [System.Text.UTF8Encoding]::new($false))
}

function TextShape($x, $y, $w, $h, $text, $size, $color = "101828", $bold = $false, $align = "l") {
  $script:id += 1
  $b = if ($bold) { '<a:b/>' } else { '' }
  $parts = ([string]$text) -split "`n"
  $runs = foreach ($part in $parts) {
    "<a:p><a:pPr algn=`"$align`"/><a:r><a:rPr lang=`"en-US`" sz=`"$($size * 100)`">$b<a:solidFill><a:srgbClr val=`"$color`"/></a:solidFill><a:latin typeface=`"Aptos`"/></a:rPr><a:t>$(Esc $part)</a:t></a:r></a:p>"
  }
@"
<p:sp>
  <p:nvSpPr><p:cNvPr id="$id" name="Text $id"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="$(Emu $x)" y="$(Emu $y)"/><a:ext cx="$(Emu $w)" cy="$(Emu $h)"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>
  <p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0"/><a:lstStyle/>$($runs -join '')</p:txBody>
</p:sp>
"@
}

function Box($x, $y, $w, $h, $fill = "FFFFFF", $line = "D0D5DD", $radius = $true) {
  $script:id += 1
  $geom = if ($radius) { "roundRect" } else { "rect" }
@"
<p:sp>
  <p:nvSpPr><p:cNvPr id="$id" name="Box $id"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="$(Emu $x)" y="$(Emu $y)"/><a:ext cx="$(Emu $w)" cy="$(Emu $h)"/></a:xfrm><a:prstGeom prst="$geom"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="$fill"/></a:solidFill><a:ln w="9000"><a:solidFill><a:srgbClr val="$line"/></a:solidFill></a:ln></p:spPr>
</p:sp>
"@
}

function Dot($x, $y, $color = "2563EB") {
  $script:id += 1
@"
<p:sp>
  <p:nvSpPr><p:cNvPr id="$id" name="Dot $id"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="$(Emu $x)" y="$(Emu $y)"/><a:ext cx="$(Emu 0.08)" cy="$(Emu 0.08)"/></a:xfrm><a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="$color"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>
</p:sp>
"@
}

function Bullet($x, $y, $items, $color = "2563EB") {
  $xml = ""
  for ($i = 0; $i -lt $items.Count; $i++) {
    $yy = $y + ($i * 0.52)
    $xml += Dot $x ($yy + 0.1) $color
    $xml += TextShape ($x + 0.22) $yy 4.2 0.36 $items[$i] 13 "101828"
  }
  $xml
}

function Node($x, $y, $w, $h, $title, $sub, $accent = "2563EB", $fill = "FFFFFF") {
  $xml = Box $x $y $w $h $fill
  $xml += Box $x $y 0.06 $h $accent $accent $false
  $xml += TextShape ($x + 0.18) ($y + 0.14) ($w - 0.35) 0.25 $title 13 "101828" $true
  $xml += TextShape ($x + 0.18) ($y + 0.45) ($w - 0.35) ($h - 0.5) $sub 9 "667085"
  $xml
}

function Metric($x, $y, $value, $label, $color = "0F766E") {
  $xml = Box $x $y 2.15 1.1
  $xml += TextShape ($x + 0.18) ($y + 0.16) 1.7 0.42 $value 24 $color $true
  $xml += TextShape ($x + 0.18) ($y + 0.64) 1.7 0.35 $label 9 "667085"
  $xml
}

function TitleBlock($kicker, $claim) {
  (TextShape 0.65 0.42 2.5 0.22 $kicker.ToUpper() 9 "2563EB" $true) +
  (TextShape 0.65 0.72 10.7 0.82 $claim 27 "101828" $true)
}

function SlideXml($num, $body) {
@"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="F8FAFC"/></a:solidFill></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="$slideW" cy="$slideH"/><a:chOff x="0" y="0"/><a:chExt cx="$slideW" cy="$slideH"/></a:xfrm></p:grpSpPr>
      $(Box 0 0 13.333 0.08 "2563EB" "2563EB" $false)
      $body
      $(TextShape 0.55 7.05 5.5 0.18 "AI-Powered Web Test Automation Platform" 7 "98A2B3")
      $(TextShape 12.25 7.05 0.5 0.18 ("{0:D2}" -f $num) 7 "98A2B3")
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>
"@
}

$slides = @()
$body = (TextShape 0.65 0.6 2.5 0.22 "FINAL YEAR PROJECT" 9 "2563EB" $true) +
  (TextShape 0.65 1.05 8.8 1.45 "AI-Powered Intelligent Web Test Automation and Analytics Platform" 34 "101828" $true) +
  (TextShape 0.68 3.02 6.8 0.75 "A browser automation platform that converts natural-language requirements into executable Playwright tests, captures evidence, and reports execution analytics." 15 "667085") +
  (Metric 0.7 5.15 "25" "automated backend tests passing" "0F766E") +
  (Metric 3.1 5.15 "3" "result states: pass, fail, warning" "2563EB") +
  (Metric 5.5 5.15 "Real" "browser execution with screenshots" "D97706") +
  (TextShape 9.9 5.75 1.9 0.3 "Viva Presentation" 13 "101828" $true)
$slides += SlideXml 1 $body

$body = (TitleBlock "Problem" "Manual web testing is powerful, but hard to scale for changing applications.") +
  (Box 0.7 1.75 5.15 4.2) + (TextShape 0.95 2.05 4.3 0.35 "Traditional automation friction" 18 "101828" $true) +
  (Bullet 1.0 2.72 @("Testers write scripts manually for every workflow.","Locators break when websites change UI structure.","Screenshots, logs, and reports are often separate.","Non-programmers cannot easily create automation.") "B42318") +
  (Box 6.7 1.75 4.65 4.2 "F0F9FF") + (TextShape 7.05 2.14 3.8 0.45 "Project idea" 20 "2563EB" $true) +
  (TextShape 7.05 2.85 3.75 1.8 "Let the user describe a testing requirement in plain English. The system should generate, execute, store, and explain the test run from one dashboard." 17 "101828")
$slides += SlideXml 2 $body

$body = (TitleBlock "Objectives" "The project combines generation, execution, evidence, and analytics in one workflow.") +
  (Node 0.72 1.92 2.48 1.9 "Generate" "Convert URL + natural language into structured steps." "2563EB") +
  (Node 3.62 1.92 2.48 1.9 "Execute" "Run steps in Chromium with Playwright automation." "0F766E") +
  (Node 6.52 1.92 2.48 1.9 "Capture" "Save screenshots, console logs, status, and duration." "D97706") +
  (Node 9.42 1.92 2.48 1.9 "Analyze" "Store history in SQLite and show pass-rate analytics." "1F2937") +
  (Box 1.3 4.55 9.4 1.05 "ECFDF3") + (TextShape 1.7 4.84 8.6 0.45 "Academic target: simple enough to demo, complete enough to show real automation behavior." 18 "0F766E" $true)
$slides += SlideXml 3 $body

$body = (TitleBlock "Architecture" "A modular backend keeps AI generation separate from browser execution and storage.") +
  (Node 0.7 2.2 1.95 1.1 "Dashboard" "HTML, CSS, JavaScript`nGenerate and run tests" "2563EB") +
  (Node 3.35 2.2 1.95 1.1 "FastAPI" "REST endpoints`nSwagger docs" "0F766E") +
  (Node 6.0 1.6 2.25 1.1 "AI Service" "Qwen via Ollama`nFallback + grounding" "D97706") +
  (Node 6.0 3.5 2.25 1.1 "Executor" "Playwright + Chromium`nScreenshots and logs" "2563EB") +
  (Node 9.15 2.2 2.15 1.1 "SQLite" "Test cases`nRun history and analytics" "0F766E") +
  (TextShape 1.25 5.25 9.2 0.6 "Service modules make AI behavior, execution behavior, database models, and API routes independently testable." 16 "101828")
$slides += SlideXml 4 $body

$body = (TitleBlock "AI Pipeline" "The generator interprets intent first, then creates executable steps with repair rules.") +
  (Node 0.7 2.35 1.95 1.9 "1. Inspect page" "Collect visible inputs, buttons, links, headings, media." "2563EB" "EFF6FF") +
  (Node 3.05 2.35 1.95 1.9 "2. Interpret prompt" "Separate test data from expected behavior." "0F766E" "F0FDF4") +
  (Node 5.4 2.35 1.95 1.9 "3. Plan workflow" "Use Qwen AI for steps, assertions, screenshots." "D97706" "EFF6FF") +
  (Node 7.75 2.35 1.95 1.9 "4. Ground selectors" "Repair invented or broad selectors using real controls." "2563EB" "F0FDF4") +
  (Node 10.1 2.35 1.95 1.9 "5. Save test" "Persist source, intent summary, expected result, and steps." "0F766E" "EFF6FF") +
  (TextShape 1.15 5.12 10.0 0.65 "If Ollama/Qwen is unavailable or invalid, deterministic fallback still creates useful tests. This avoids a blank or broken demo." 16 "101828")
$slides += SlideXml 5 $body

$body = (TitleBlock "Execution" "Playwright turns generated steps into browser evidence, not just text output.") +
  (Node 0.8 1.9 3.0 1.18 "Actions" "goto, click, fill, press, wait" "2563EB") +
  (Node 0.8 3.52 3.0 1.18 "Assertions" "title, text, URL, visible element, value, count" "0F766E") +
  (Node 4.45 1.9 3.0 1.18 "Evidence" "screenshots, console logs, duration" "D97706") +
  (Node 4.45 3.52 3.0 1.18 "Resilience" "popup dismissal, selector recovery, warning state" "2563EB") +
  (Metric 8.35 2.0 "Pass" "workflow completed" "0F766E") +
  (Metric 8.35 3.35 "Fail" "required step failed" "B42318") +
  (Metric 8.35 4.7 "Warning" "main flow completed with skipped optional step" "D97706")
$slides += SlideXml 6 $body

$body = (TitleBlock "Dashboard" "The user experience is intentionally simple: generate, inspect, run, and review.") +
  (Box 0.75 1.82 4.75 4.3) + (TextShape 1.05 2.15 3.6 0.34 "Main controls" 18 "101828" $true) +
  (Bullet 1.12 2.78 @("Website URL input","Natural language requirement","Inspect & Generate Test","Run Latest and Run Generated Suite","Optional visible browser mode") "2563EB") +
  (Box 6.5 1.82 4.75 4.3 "F8FAFC") + (TextShape 6.8 2.15 3.6 0.34 "Review panels" 18 "101828" $true) +
  (Bullet 6.88 2.78 @("Saved tests with step list","AI/fallback source label","Execution status and duration","Logs and screenshots","Analytics counts and pass rate") "0F766E")
$slides += SlideXml 7 $body

$body = (TitleBlock "Validation" "The system is covered by automated backend tests and live browser verification.") +
  (Metric 0.9 1.95 "25" "pytest tests passing" "0F766E") +
  (Metric 3.4 1.95 "Qwen" "AI intent + plan generation tested" "2563EB") +
  (Metric 5.9 1.95 "Suite" "multi-case generation tested" "D97706") +
  (Metric 8.4 1.95 "Live" "Flipkart flows verified" "0F766E") +
  (Box 1.2 3.9 9.4 1.55) + (TextShape 1.55 4.2 8.5 0.34 "Recent robustness fixes" 18 "101828" $true) +
  (TextShape 1.55 4.72 8.55 0.55 "Popup dismissal, generic link repair, Flipkart OTP login handling, screenshot fallback, noisy console filtering, and URL checks that do not wait for slow external assets." 14 "667085")
$slides += SlideXml 8 $body

$body = (TitleBlock "Limits & Future" "The platform is complete for demonstration, with clear paths to production hardening.") +
  (Box 0.8 1.85 4.9 4.1 "FFF7ED") + (TextShape 1.1 2.18 3.6 0.32 "Current limitations" 18 "D97706" $true) +
  (Bullet 1.18 2.88 @("Local AI quality depends on Ollama/Qwen availability.","Public sites can change selectors and anti-bot behavior.","SQLite is best for academic/demo scope.","Advanced report export is future work.") "D97706") +
  (Box 6.45 1.85 4.9 4.1 "ECFDF3") + (TextShape 6.75 2.18 3.6 0.32 "Future scope" 18 "0F766E" $true) +
  (Bullet 6.83 2.88 @("PostgreSQL and multi-user accounts.","CI/CD integration for scheduled test runs.","PDF/HTML execution reports.","Parallel browser execution and visual regression.") "0F766E")
$slides += SlideXml 9 $body

$body = (TitleBlock "Viva Demo" "A short demo can prove generation, execution, evidence, and analytics end to end.")
$demo = @(
  @("1","Open /app","Show the dashboard and analytics cards."),
  @("2","Generate test","Use Flipkart or example.com with a natural prompt."),
  @("3","Inspect steps","Explain intent summary, source label, and expected result."),
  @("4","Run test","Show logs, status, duration, and screenshots."),
  @("5","Explain design","Map the run back to FastAPI, Qwen, Playwright, SQLite.")
)
for ($i = 0; $i -lt $demo.Count; $i++) {
  $y = 1.7 + ($i * 0.92)
  $body += Dot 0.92 ($y + 0.20) "2563EB"
  $body += Node 1.6 $y 9.1 0.62 $demo[$i][1] $demo[$i][2] @("2563EB","0F766E","D97706","2563EB","0F766E")[$i]
}
$body += TextShape 1.1 6.42 9.7 0.3 "Closing line: AI reduces script-writing effort, while Playwright and evidence capture keep the tests verifiable." 14 "101828" $true
$slides += SlideXml 10 $body

for ($i = 0; $i -lt $slides.Count; $i++) {
  New-Item -ItemType Directory -Force -Path (Join-Path $work "ppt\slides") | Out-Null
  New-Item -ItemType Directory -Force -Path (Join-Path $work "ppt\slides\_rels") | Out-Null
  WriteText (Join-Path $work "ppt\slides\slide$($i + 1).xml") $slides[$i]
  WriteText (Join-Path $work "ppt\slides\_rels\slide$($i + 1).xml.rels") '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
}

@(
  "$work\_rels",
  "$work\docProps",
  "$work\ppt",
  "$work\ppt\_rels",
  "$work\ppt\theme",
  "$work\ppt\slideMasters",
  "$work\ppt\slideMasters\_rels",
  "$work\ppt\slideLayouts",
  "$work\ppt\slideLayouts\_rels"
) | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }

$contentTypesSlides = (1..10 | ForEach-Object { "<Override PartName=""/ppt/slides/slide$_.xml"" ContentType=""application/vnd.openxmlformats-officedocument.presentationml.slide+xml""/>" }) -join "`n"
WriteText "$work\[Content_Types].xml" @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  $contentTypesSlides
</Types>
"@

$rels = (1..10 | ForEach-Object { "<Relationship Id=""rId$($_ + 2)"" Type=""http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"" Target=""slides/slide$_.xml""/>" }) -join "`n"
$sldIds = (1..10 | ForEach-Object { "<p:sldId id=""$($_ + 255)"" r:id=""rId$($_ + 2)""/>" }) -join "`n"
WriteText "$work\_rels\.rels" '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>'
WriteText "$work\ppt\_rels\presentation.xml.rels" @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
  $rels
</Relationships>
"@
WriteText "$work\ppt\presentation.xml" @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>$sldIds</p:sldIdLst>
  <p:sldSz cx="$slideW" cy="$slideH" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle><a:defPPr><a:defRPr lang="en-US"/></a:defPPr></p:defaultTextStyle>
</p:presentation>
"@
WriteText "$work\ppt\theme\theme1.xml" '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Viva Theme"><a:themeElements><a:clrScheme name="Viva"><a:dk1><a:srgbClr val="101828"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F2937"/></a:dk2><a:lt2><a:srgbClr val="F8FAFC"/></a:lt2><a:accent1><a:srgbClr val="2563EB"/></a:accent1><a:accent2><a:srgbClr val="0F766E"/></a:accent2><a:accent3><a:srgbClr val="D97706"/></a:accent3><a:accent4><a:srgbClr val="B42318"/></a:accent4><a:accent5><a:srgbClr val="667085"/></a:accent5><a:accent6><a:srgbClr val="D0D5DD"/></a:accent6><a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="0F766E"/></a:folHlink></a:clrScheme><a:fontScheme name="Aptos"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme><a:fmtScheme name="Default"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9000"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'
WriteText "$work\ppt\slideMasters\slideMaster1.xml" '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="6858000"/><a:chOff x="0" y="0"/><a:chExt cx="12192000" cy="6858000"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
WriteText "$work\ppt\slideMasters\_rels\slideMaster1.xml.rels" '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>'
WriteText "$work\ppt\slideLayouts\slideLayout1.xml" '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="6858000"/><a:chOff x="0" y="0"/><a:chExt cx="12192000" cy="6858000"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
WriteText "$work\ppt\slideLayouts\_rels\slideLayout1.xml.rels" '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>'
WriteText "$work\docProps\core.xml" '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>AI Web Test Automation Viva</dc:title><dc:creator>Codex</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy></cp:coreProperties>'
WriteText "$work\docProps\app.xml" '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Microsoft PowerPoint</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>10</Slides></Properties>'

if (Test-Path $out) { Remove-Item -LiteralPath $out -Force }
$zip = Join-Path $root "docs\AI-Web-Test-Automation-Viva.zip"
if (Test-Path $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -Path "$work\*" -DestinationPath $zip -Force
Move-Item -LiteralPath $zip -Destination $out -Force
Write-Host "Created $out"
