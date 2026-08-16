;===============================================================================
; Name:			Minime
; Author:		Tijs Hendriks - http://www.saphua.com/
; Description:	Minimizes windows to a single tray icon
;===============================================================================

#NoTrayIcon

; Includes
#Include <Array.au3>
#include <ButtonConstants.au3>
#include <GUIConstantsEx.au3>
#include <EditConstants.au3>
#include <Misc.au3>
#include <StaticConstants.au3>
#include <String.au3>
#include <WindowsConstants.au3>
; UDF
#include <ModernMenuRaw.au3>
#include <HotKeySelect.au3>

; AutoIt options
AutoItSetOption("TrayAutoPause", 0)
AutoItSetOption("TrayMenuMode", 1)
AutoItSetOption("WinTitleMatchMode", 4)
OnAutoItExitRegister("OnExit")

; Version information
global const $VERSION_CODE = "2.2"
global const $APPLICATION_NAME = "Minime"
global const $FULL_NAME = $APPLICATION_NAME & " v" & $VERSION_CODE
global const $PAGE_URL = "http://www.saphua.com/minime/"

global const $SINGLETON_ID = "minime4d7ftnb8"
global const $AUTOIT_TITLE = "minimej41ksqn4"

; Singleton check
if _Singleton("minime", 1) == 0 then
	if MsgBox(1, $FULL_NAME, "An instance of " & $APPLICATION_NAME & " is already running." & @CR & "Press OK to close the previous instance and start this one." & @CR & "(This will restore all previously minimized windows)") == 1 then
		WinClose($AUTOIT_TITLE)
	else
		exit 0
	endif
endif

; Unique title
AutoItWinSetTitle($AUTOIT_TITLE)

; Used by ModernMenuRaw.au3
$bUseAdvTrayMenu = false

;===============================================================================
; Declare constant vars
;===============================================================================
if not IsDeclared("WM_GETICON") then global const $WM_GETICON = 0x007F
if not IsDeclared("GCL_HICONSM") then global const $GCL_HICONSM = -34
if not IsDeclared("GCL_HICON") then global const $GCL_HICON = -14
if not IsDeclared("PROCESS_QUERY_INFORMATION") then global const $PROCESS_QUERY_INFORMATION = 0x0400
if not IsDeclared("PROCESS_VM_READ") then global const $PROCESS_VM_READ = 0x0010
global const $SHORTCUT_FILE = @StartupDir & "\Minime.lnk"
global const $INI_FILE = @ScriptDir & "/settings.ini" ; Location of ini file
global const $ICO_DST = @TempDir ; Directory where icons are saved in
global const $ICO_MINIME = $ICO_DST & "/minime.ico"
global const $ICO_ABOUT =  $ICO_DST & "/about.ico"
global const $ICO_CLOSE = $ICO_DST & "/close.ico"
global const $ICO_DEFAULT = $ICO_DST & "/default.ico"
global const $ICO_RESTORE = $ICO_DST & "/restore.ico"
global const $MAX_WINDOWS = 20 ; Maximum amount of windows that can be minimized
global const $DEFAULT_HOTKEY = "^+z"
global const $DEFAULT_SHOWALL_KEY = "^+a"

;===============================================================================
; Declare vars
;===============================================================================
dim $itemWindow[$MAX_WINDOWS] ; Array that contains handles to windows
dim $itemTray[$MAX_WINDOWS] ; Array that contains handles to context items
$itemCount = 0
$checkTimer = TimerInit()

;===============================================================================
; Ini Settings
;===============================================================================
$hotkey = IniRead($INI_FILE, "main", "hotkey", $DEFAULT_HOTKEY)
$showall = IniRead($INI_FILE, "main", "showall", $DEFAULT_SHOWALL_KEY)
ApplyHotkeys()

;===============================================================================
; Icons
;===============================================================================
FileInstall("ico/minime.ico", $ICO_MINIME, 1)
FileInstall("ico/about.ico", $ICO_ABOUT, 1)
FileInstall("ico/close.ico", $ICO_CLOSE, 1)
FileInstall("ico/default.ico", $ICO_DEFAULT, 1)
FileInstall("ico/restore.ico", $ICO_RESTORE, 1)

;===============================================================================
; Tray and context items
;===============================================================================
$mainIcon = _TrayIconCreate($FULL_NAME, $ICO_MINIME)
_TrayIconSetState()
_TrayCreateContextMenu()
_TrayCreateItem("")
$showAllTray = _TrayCreateItem("Show All")
_TrayItemSetIcon($showAllTray, $ICO_RESTORE)
$optionsTray = _TrayCreateItem("Options")
_TrayItemSetIcon($optionsTray, $ICO_ABOUT)
_TrayCreateItem("")
$closeTray = _TrayCreateItem("Close")
_TrayItemSetIcon($closeTray, $ICO_CLOSE)

;===============================================================================
; Crappy way of checking if Minime has sufficient rights
;===============================================================================
$testfile = "temp" & Random(10000, 99999, 1)
IniWrite($testfile, "admin", "admin", "true")
if IniRead($testfile, "admin", "admin", "false") <> "true" then
	_TrayTip($mainIcon, $FULL_NAME, $APPLICATION_NAME & " requires administrator rights in order to save settings.")
endif
FileDelete($testfile)

;===============================================================================
; Main loop
;===============================================================================
while true
	; GUI message
    $msg = GUIGetMsg()
    if $msg <> 0 then
		if $msg == $closeTray then
			Close()
		elseif $msg == $showAllTray then
			ShowAll()
		elseif $msg == $optionsTray then
			ShowOptions()
		else
			for $i = 0 to $MAX_WINDOWS - 1
				if $msg == $itemTray[$i] and $itemTray[$i] <> "" then
					DisplayItem($i)
					exitloop
				endif
			next
		endif
	endif
	; Check items
	if TimerDiff($checkTimer) > 1000 then
		CheckItems()
		$checkTimer = TimerInit()
	endif
wend

;===============================================================================
; Options form
;===============================================================================
func ShowOptions()
	; Disables current hotkeys
	HotKeySet($hotkey)
	HotKeySet($showall)
	
	; UI
	local $optionsForm = GUICreate($FULL_NAME & " - Options", 326, 226)
	GUICtrlCreateGroup("About", 8, 8, 310, 53)
	GUICtrlCreateLabel("Author: Tijs Hendriks - SaphuA", 16, 24, 260, 17)
	local $websiteLabel = GUICtrlCreateLabel($PAGE_URL, 16, 40, 260, 17)
	GUICtrlSetColor($websiteLabel, 0x0000FF)
	GUICtrlSetCursor($websiteLabel, 0)
	
	GUICtrlCreateGroup("Options", 8, 64, 310, 155)
	GUICtrlCreateLabel("Minimize window:", 16, 109, 90, 17, $SS_RIGHT)
	local $hotkeyButton = GUICtrlCreateButton("Set", 109, 104, 40, 22)
	local $hotkeyInput = GUICtrlCreateInput($hotkey, 152, 104, 154, 22, $ES_READONLY)
	GUICtrlCreateLabel("Show all:", 16, 136, 90, 17, $SS_RIGHT)
	local $showallButton = GUICtrlCreateButton("Set", 109, 132, 40, 22)
	local $showallInput = GUICtrlCreateInput($showall, 152, 132, 154, 22, $ES_READONLY)

	local $winCheckBox = GUICtrlCreateCheckbox("Advanced", 154, 160, 90, default)
	local $saveButton = GUICtrlCreateButton("Save", 152, 188, 75, 25)
	local $cancelButton = GUICtrlCreateButton("Cancel", 231, 188, 75, 25)
	
	; Checks if autorun is enabled or not
	local $startCheckBox = GUICtrlCreateCheckbox("Launch " & $APPLICATION_NAME & " when Windows starts", 16, 79, 260)
	if FileExists($SHORTCUT_FILE) then
		local $shortcut = FileGetShortcut($SHORTCUT_FILE)
		if $shortcut[0] == @AutoItExe then
			GUICtrlSetState($startCheckBox, $GUI_CHECKED)
		endif
	endif
	
	GUISetIcon($ICO_MINIME)
	GUISetState()
	
	while true
		local $msg = GUIGetMsg()
		if $msg == $websiteLabel then
			ShellExecute($PAGE_URL)
		elseif $msg == $hotkeyButton then
			ShowHotkeyForm($hotkeyInput, $optionsForm)
		elseif $msg == $showallButton then
			ShowHotkeyForm($showallInput, $optionsForm)
		elseif $msg == $saveButton then
			; Saves and applies hotkey settings
			$hotkey = GUICtrlRead($hotkeyInput)
			$showall = GUICtrlRead($showallInput)
			ApplyHotkeys()
			
			IniWrite($INI_FILE, "main", "hotkey", $hotkey)
			IniWrite($INI_FILE, "main", "showall", $showall)
			
			; Saves autorun settings
			if BitAND(GUICtrlRead($startCheckBox), $GUI_CHECKED) then
				FileCreateShortcut(@AutoItExe, $SHORTCUT_FILE, @ScriptDir, default, default, @AutoItExe)
			else
				FileDelete($SHORTCUT_FILE)
			endif
			exitloop
		elseif $msg == $cancelButton then
			ApplyHotkeys()
			exitloop
		elseif $msg == $winCheckBox then
			if BitAND(GUICtrlRead($winCheckBox), $GUI_CHECKED) then
				GUICtrlSetStyle($hotkeyInput, $GUI_SS_DEFAULT_INPUT)
				GUICtrlSetStyle($showallInput, $GUI_SS_DEFAULT_INPUT)
			else
				GUICtrlSetStyle($hotkeyInput, $ES_READONLY)
				GUICtrlSetStyle($showallInput, $ES_READONLY)
			endif
		endif
		if $msg == $GUI_EVENT_CLOSE then
			ApplyHotkeys()
			exitloop
		endif
	wend
	GUIDelete($optionsForm)
endfunc

;===============================================================================
; Hotkey selection form
;===============================================================================
func ShowHotkeyForm($target, $parent)
	; UI
	WinSetState($parent, "", @SW_DISABLE)
	local $hotkeyForm = GUICreate("Set Hotkey", 312, 64, -1, -1, -1, -1, $parent)
	local $winCheckBox = GUICtrlCreateCheckbox("WIN-Key +", 3, 3)
	local $hotkeyControl = _WinAPI_CreateWindowEx(0, "msctls_hotkey32", "", $WS_CHILD + $WS_VISIBLE, 74, 3, 234, 22, $hotkeyForm)
	local $saveButton = GUICtrlCreateButton("Save", 152, 35, 75, 25)
	local $cancelButton = GUICtrlCreateButton("Cancel", 231, 35, 75, 25)
	_WinAPI_SetFocus($hotkeyControl)
	GUISetIcon($ICO_MINIME)
	GUISetState()
	
	local $result = ""
	while true
		local $msg = GUIGetMsg()
		switch $msg
			case $saveButton
				; Formats the hotkey
				local $x = _GetHotKey($hotkeyControl)
				if $x = "" then
					$result = ""
				elseif BitAND(GUICtrlRead($winCheckBox), $GUI_CHECKED) = $GUI_CHECKED then
					$result = "#" & $x
				else
					$result = $x
				endif
				exitloop
			case $cancelButton, $GUI_EVENT_CLOSE
				$result = -1
				exitloop
		endswitch
	wend
	
	if $result <> -1 then
		GuiCtrlSetData($target, $result)
	endif
	
	GUIDelete($hotkeyForm)
	WinSetState($parent, "", @SW_ENABLE)
	WinActivate($parent)
endfunc

;===============================================================================
; Minimizes a window
; This function will hide a window and add it to minime's context menu
; It ignore some hard coded OS windows and it also contains a check to make sure the same
; window is not minimized twice
;===============================================================================
func Minimize($winHn)
	if $winHn == "" then
	elseif $WinHn == WinGetHandle("[TITLE:Options; CLASS:AutoIt v3 GUI]") then
	elseif $WinHn == WinGetHandle("[TITLE:Set Hotkey; CLASS:AutoIt v3 GUI]") then
	elseif $WinHn == WinGetHandle("[CLASS:Shell_TrayWnd]") then
	elseif $WinHn == WinGetHandle("[CLASS:DV2ControlHost]") then
	elseif $WinHn == WinGetHandle("[CLASS:Progman]") then
	elseif $WinHn == WinGetHandle("[CLASS:Desktop User Picture]") then
	elseif _ArraySearch($itemWindow, $winHn) >= 0 then
	else
		for $i = 0 to $MAX_WINDOWS - 1
			if $itemWindow[$i] == "" then
				$itemWindow[$i] = $winHn
				$itemTray[$i] = _TrayCreateItem(WinGetTitle($winHn), -1, 0)
				_TrayItemSetIcon($itemTray[$i], GetIcon($winHn))
				WinSetState($winHn, "", @SW_HIDE)
				$itemCount += 1
				exitloop
			endif
		next
	endif
endfunc

func MinimizeActive()
	Minimize(WinGetHandle("[ACTIVE]"))
endfunc

;===============================================================================
; Makes sure the settings are correct by reapplying hotkeys
;===============================================================================
func ApplyHotkeys()
	HotKeySet($hotkey)
	if StringLen($hotkey) > 0 then
		HotKeySet($hotkey, "MinimizeActive")
	endif
	
	HotKeySet($showall)
	if StringLen($showall) > 0 then
		HotKeySet($showall, "ShowAll")
	endif
endfunc

;===============================================================================
; Checks if an item should be removed because its target window was closed or
; restored and updates the title of an item in case the window title changed
;===============================================================================
func CheckItems()
	if $itemCount > 0 then
		for $i = 0 to $MAX_WINDOWS - 1
			if $itemWindow[$i] <> "" then
				; Deletes the item
				if not WinExists($itemWindow[$i]) or BitAND(WinGetState($itemWindow[$i]), 2) then
					DeleteItemTray($i)
				; Updates the title text
				elseif WinGetTitle($itemWindow[$i]) <> _GetMenuText($itemTray[$i]) then
					_TrayItemSetText($itemTray[$i], WinGetTitle($itemWindow[$i]))
				endif
			endif
		next
	endif
endfunc

;===============================================================================
; Displays all windows and removes all items
;===============================================================================
func ShowAll()
	if IsDeclared("MAX_WINDOWS") then
		for $i = 0 to $MAX_WINDOWS - 1
			if $itemWindow[$i] <> "" then
				DisplayItem($i)
			endif
		next
	endif
endfunc

;===============================================================================
; Displays a window and removes its item
;===============================================================================
func DisplayItem($i)
	WinSetState($itemWindow[$i], "", @SW_SHOW)
	DeleteItemTray($i)
endfunc

;===============================================================================
; Removes an item
;===============================================================================
func DeleteItemTray($i)
	_TrayDeleteItem($itemTray[$i])
	$itemWindow[$i] = ""
	$itemTray[$i] = ""
	$itemCount -= 1
endfunc

;===============================================================================
; Closes Minime
;===============================================================================
func Close()
	exit
endfunc

func OnExit()
	ShowAll()
	OnAutoItExit()
endfunc

;===============================================================================
; Thanks to (please let me know)
; Gets an icon from a target window to use in the context menu
;===============================================================================
func GetIcon($winHn)
	local $nID, $nResult
	local $sFile = ""
	local $hIcon = DllCall("user32.dll", "hwnd", "SendMessage", "hwnd", $winHn, "int", $WM_GETICON, "long", 2, "long", 0)
	$hIcon = $hIcon[0]
	if $hIcon = 0 then
		$hIcon = DllCall("user32.dll", "hwnd", "SendMessage", "hwnd", $winHn, "int", $WM_GETICON, "long", 0, "long", 0)
		$hIcon = $hIcon[0]
	endif
	if $hIcon = 0 then GetClassLong($winHn, $GCL_HICONSM)
	if $hIcon = 0 then GetClassLong($winHn, $GCL_HICON)
	if $hIcon = 0 then $sFile = @AutoItExe
	if $hIcon = 0 then
		local $nPID = WinGetProcess($winHn)
		if $nPID <> -1 then
			local $hProc = OpenProcess(BitOR($PROCESS_QUERY_INFORMATION, $PROCESS_VM_READ), 0, $nPID)
			if $hProc <> 0 then
				local $stMod = DllStructCreate("int[1024]")
				local $stSize = DllStructCreate("dword")
				$nResult = EnumProcessModules($hProc, DllStructGetPtr($stMod), DllStructGetSize($stMod), DllStructGetPtr($stSize))
				if $nResult <> 0 then
					local $stPath = DllStructCreate("char[260]")
					if GetModuleFileNameExA($hProc, DllStructGetData($stMod, 1), DllStructGetPtr($stPath), DllStructGetSize($stPath)) <> 0 then
						$sFile = DllStructGetData($stPath, 1)
						return $sFile
					endif
				endif
			endif
		endif
	else
		return $hIcon
	endif
	return $ICO_DEFAULT
endfunc

func GetClassLong($winHn, $nIdx)
	local $hResult = DllCall("user32.dll", "hwnd", "GetClassLong", "hwnd", $winHn, "int", $nIdx)
	return $hResult[0]
endfunc

func OpenProcess($nAccess, $nHandle, $nPID)
	local $hResult = DllCall("kernel32.dll", "hwnd", "OpenProcess", "dword", $nAccess, "int", $nHandle, "dword", $nPID)
	return $hResult[0]
endfunc

func EnumProcessModules($hProc, $pModule, $nSize, $pReqSize)
	local $nResult = DllCall("psapi.dll", "dword", "EnumProcessModules", "hwnd", $hProc, "ptr", $pModule, "dword", $nSize, "ptr", $pReqSize)
	return $nResult[0]
endfunc

func GetModuleFileNameExA($hProc, $hModule, $pFileName, $nSize)
	local $nResult = DllCall("psapi.dll", "dword", "GetModuleFileNameExA", "hwnd", $hProc, "hwnd", $hModule, "ptr", $pFileName, "dword", $nSize)
	return $nResult[0]
endfunc
