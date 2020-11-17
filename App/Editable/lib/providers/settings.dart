import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class Settings with ChangeNotifier {
  bool _preprocessing;

  Future<bool> get preprocessing async {
    if (_preprocessing == null) {
      final prefs = await SharedPreferences.getInstance();
      _preprocessing = prefs.getBool('preprocessing') ?? false;
    }
    return _preprocessing;
  }

  Future<void> setPreprocessing(bool newValue) async {
    _preprocessing = newValue;
    final prefs = await SharedPreferences.getInstance();
    prefs.setBool('preprocessing', _preprocessing);
    notifyListeners();
  }

  Future<void> fetchAndSetSettings() async {
    final prefs = await SharedPreferences.getInstance();
    _preprocessing = prefs.getBool('preprocessing') ?? false;
    notifyListeners();
  }
}
