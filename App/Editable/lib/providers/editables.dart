import 'package:flutter/material.dart';

import '../helpers/db_helper.dart';

class Editable {
  final String id;
  final String text;

  const Editable(this.id, this.text);
}

class Editables with ChangeNotifier {
  List<Editable> _items = [];

  List<Editable> get items {
    return [..._items];
  }

  void addEditable(String text) {
    String id = UniqueKey().toString();
    final item = Editable(id, text);
    _items.add(item);
    DBHelper.insert({
      'id': id,
      'text': text,
    });
    notifyListeners();
  }

  void removeById(String id) {
    _items.removeWhere((element) => element.id == id);
    DBHelper.delete(id);
    notifyListeners();
  }

  Editable getById(String id) {
    return _items.firstWhere((element) => element.id == id);
  }

  void setTextById(String id, String text) {
    final index = _items.indexWhere((element) => element.id == id);
    _items.removeAt(index);
    final item = Editable(id, text);
    _items.insert(index, item);
    DBHelper.insert({
      'id': item.id,
      'text': item.text,
    });
    notifyListeners();
  }

  Future<void> fetchAndSetEditables() async {
    final dataList = await DBHelper.getData();
    _items = dataList
        .map(
          (item) => Editable(
            item['id'],
            item['text'],
          ),
        )
        .toList();
    notifyListeners();
  }
}
