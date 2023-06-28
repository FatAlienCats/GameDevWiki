
"""
scriptToShelf "test" "\nimport importlib\nimport ml_softWeights\nimportlib.reload(ml_softWeights)\nml_softWeights.ui()\n" "0";
setShelfStyle `optionVar -query shelfItemStyle` `optionVar -query shelfItemSize`;
string $gParentPopupMenu = `popupMenu`;popupMenu -e -pmo 1 -pmc ( "shelfButtonPMO \"" + $gParentPopupMenu + "\" 1 " + "\"shelfButton27\" \"/*dSBRMBMI*/\"" ) $gParentPopupMenu;
// Result: Shelf|MainShelfLayout|formLayout17|ShelfLayout|Custom||popupMenu130
"""