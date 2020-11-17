import 'dart:convert';
import 'dart:io';
import 'dart:async';

import 'package:http/http.dart' as http;

class HTTPHelper {
  static const baseUrl = '192.168.0.112:8080';

  static Future<String> sendPostImageRequest(
    String b64Image,
    bool preprocessing,
  ) async {
    final uri = Uri.http(baseUrl, '/convert');
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
}
