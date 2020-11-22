import 'dart:convert';
import 'dart:io';

import 'package:Editable/helpers/file_helper.dart';
import 'package:http/http.dart' as http;

class HttpHelper {
  static const baseUrl = '192.168.0.112:8080';

  static Future<String> sendPostImageRequest(
    String b64Image,
    bool preprocessing,
  ) async {
    final uri = Uri.http(baseUrl, '/image_to_text');
    try {
      final response = await http.post(uri,
          body: json.encode(
            {'b64image': b64Image, 'preprocessing': preprocessing},
          ),
          headers: {
            HttpHeaders.hostHeader: baseUrl,
            HttpHeaders.dateHeader: DateTime.now().toIso8601String(),
            HttpHeaders.contentTypeHeader: ContentType.json.mimeType,
          });
      final respText = json.decode(response.body)['result'];
      print(response.body);
      return respText;
    } catch (error) {
      print('################ERROR################');
      print(error);
      print('#####################################');
      throw error;
    }
  }

  static Future<File> sendGetDocxFromText(String text) async {
    final uri = '${Uri.http(baseUrl, '/text_to_docx')}/${_urlify(text)}';
    try {
      final response = await http.get(uri, headers: {
        HttpHeaders.hostHeader: baseUrl,
        HttpHeaders.dateHeader: DateTime.now().toIso8601String(),
      });
      if (response.statusCode == 200) {
        final file = await FileHelper.writeFile(response.bodyBytes);
        return file;
      }
      throw HttpException('status code: ${response.statusCode}');
    } catch (error) {
      print('################ERROR################');
      print(error);
      print('#####################################');
      throw error;
    }
  }

  static String _urlify(String str) {
    return str.replaceAll(RegExp(r' '), '%20');
  }
}

class HttpException with Exception {
  String message;
  HttpException(this.message);
}
