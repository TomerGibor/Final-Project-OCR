import 'package:sqflite/sqflite.dart' as sql;
import 'package:sqflite/sqlite_api.dart';
import 'package:path/path.dart' as path;

class DBHelper {
  static const DB_NAME = 'editables';

  static Future<Database> database() async {
    final dbPath = await sql.getDatabasesPath();
    return sql.openDatabase(path.join(dbPath, DB_NAME),
        onCreate: (db, version) {
      return db
          .execute('CREATE TABLE editables (id TEXT PRIMARY KEY, text TEXT)');
    }, version: 1);
  }

  static Future<void> insert(Map<String, Object> data) async {
    final db = await DBHelper.database();
    db.insert(
      DB_NAME,
      data,
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  static Future<void> delete(String id) async {
    final db = await DBHelper.database();
    int count = await db.delete(DB_NAME, where: 'id = ?', whereArgs: [id]);
    assert(count == 1);
  }

  static Future<List<Map<String, dynamic>>> getData() async {
    final db = await DBHelper.database();
    return db.query(DB_NAME);
  }
}
