import 'package:flutter/material.dart';
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

class Themes {
  static ThemeData themeData(
      BuildContext context, bool isDarkTheme, double fontSizeFactor) {
    return ThemeData(
      primaryColor: isDarkTheme ? Colors.teal : Colors.indigo,
      accentColor: isDarkTheme ? Colors.indigo : Colors.deepOrange,
      cardColor: isDarkTheme ? Colors.grey[900] : Colors.white,
      brightness: isDarkTheme ? Brightness.dark : Brightness.light,
      buttonTheme: Theme.of(context).buttonTheme.copyWith(
            colorScheme: isDarkTheme ? ColorScheme.dark() : ColorScheme.light(),
          ),
      visualDensity: VisualDensity.adaptivePlatformDensity,
      textTheme: Theme.of(context).textTheme.apply(
            fontSizeFactor: fontSizeFactor,
            bodyColor: isDarkTheme ? Colors.white : Colors.black,
            displayColor: isDarkTheme ? Colors.white70 : Colors.black54,
          ),
    );
  }
}
