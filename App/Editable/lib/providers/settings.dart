import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class Settings with ChangeNotifier {
  final preprocessingKey = 'preprocessing';
  final darkThemeKey = 'darkTheme';
  final fontSizeFactorKey = 'fontSizeFactor';
  final fontSizeDefaultFactor = 1.1;

  bool _preprocessing;
  bool _darkTheme;
  double _fontSizeFactor;
  SharedPreferences _prefs;

  Settings() {
    _preprocessing = true;
    _darkTheme = false;
    _fontSizeFactor = fontSizeDefaultFactor;
    loadFromPrefs();
  }

  bool get preprocessing => _preprocessing;
  double get fontSizeFactor => _fontSizeFactor;
  bool get darkTheme => _darkTheme;

  void togglePreprocessing() {
    _preprocessing = !_preprocessing;
    saveToPrefs();
    notifyListeners();
  }

  void toggleDarkTheme() {
    _darkTheme = !_darkTheme;
    saveToPrefs();
    notifyListeners();
  }

  void setFontSize(double newValue) {
    _fontSizeFactor = newValue;
    saveToPrefs();
    notifyListeners();
  }

  Future<void> initPrefs() async {
    if (_prefs == null) {
      _prefs = await SharedPreferences.getInstance();
    }
  }

  Future<void> loadFromPrefs() async {
    await initPrefs();
    _preprocessing = _prefs.getBool(preprocessingKey) ?? false;
    _darkTheme = _prefs.getBool(darkThemeKey) ?? false;
    _fontSizeFactor =
        _prefs.getDouble(fontSizeFactorKey) ?? fontSizeDefaultFactor;
    notifyListeners();
  }

  Future<void> saveToPrefs() async {
    await initPrefs();
    _prefs.setBool(preprocessingKey, _preprocessing);
    _prefs.setBool(darkThemeKey, _darkTheme);
    _prefs.setDouble(fontSizeFactorKey, _fontSizeFactor);
  }
}
