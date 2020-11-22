import 'dart:io';
import 'dart:typed_data';

import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:ext_storage/ext_storage.dart';

class FileHelper {
  static Future<String> get _localPath async {
    if (Platform.isAndroid) {
      return ExtStorage.getExternalStoragePublicDirectory(
          ExtStorage.DIRECTORY_DOWNLOADS);
    }
    // Platform is iOS
    final dir = await getApplicationDocumentsDirectory();
    return dir.path;
  }

  static Future<void> _requestPermissions() async {
    var status = await Permission.storage.status;

    if (status.isGranted) {
      return;
    } else {
      status = await Permission.storage.request();
    }
    if (!status.isGranted) {
      throw PermissionDeniedException();
    }
  }

  static Future<File> get _file async {
    final path = await _localPath;
    return File('$path/Editable document.docx');
  }

  static Future<File> writeFile(Uint8List bytes) async {
    final file = await _file;
    await _requestPermissions();
    return file.writeAsBytes(List.from(bytes));
  }
}

class PermissionDeniedException with Exception {}
