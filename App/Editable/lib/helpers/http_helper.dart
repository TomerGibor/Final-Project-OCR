import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:Editable/helpers/file_helper.dart';
import 'package:http/http.dart' as http;

class HttpHelper {
  static const baseUrl = '192.168.0.100:8080';

  static Future<String> sendPostImageRequest(String b64Image,
      [List<Point<double>> points]) async {
    final uri = Uri.http(baseUrl, '/image_to_text');
    try {
      final response = await http.post(uri,
          body: json.encode(
            points == null
                ? {'b64image': b64Image}
                : {'b64image': b64Image, 'points': _serializePoints(points)},
          ),
          headers: {
            HttpHeaders.hostHeader: baseUrl,
            HttpHeaders.dateHeader: DateTime.now().toIso8601String(),
            HttpHeaders.contentTypeHeader: ContentType.json.mimeType,
          });

      if (response.statusCode == 200) {
        final respText = json.decode(response.body)['result'];
        return respText;
      }
      throw HttpException(
          'status code: ${response.statusCode}, message: ${response.body}');
    } catch (error) {
      print('################ERROR################');
      print(error);
      print('#####################################');
      throw error;
    }
  }

  static Future<List<Point<double>>> sendGetPointsRequest(
      String b64Image) async {
    final uri = Uri.http(baseUrl, '/find_page_points');
    try {
      final response = await http.post(uri,
          body: json.encode(
            {'b64image': b64Image},
          ),
          headers: {
            HttpHeaders.hostHeader: baseUrl,
            HttpHeaders.dateHeader: DateTime.now().toIso8601String(),
            HttpHeaders.contentTypeHeader: ContentType.json.mimeType,
          });

      if (response.statusCode == 200) {
        List<dynamic> points = json.decode(response.body)['points'];
        List<Map<String, int>> newPoints = [];
        points.forEach((element) {
          newPoints.add({'x': element['x'].toInt(), 'y': element['y'].toInt()});
        });
        return _deserializePoints(newPoints);
      }
      throw HttpException(
          'status code: ${response.statusCode}, message: ${response.body}');
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
      throw HttpException(
          'status code: ${response.statusCode}, message: ${response.body}');
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

  static List<Map<String, int>> _serializePoints(List<Point<double>> points) {
    List<Map<String, int>> serializedPoints = [];
    for (var pt in points) {
      serializedPoints.add({'x': pt.x.toInt(), 'y': pt.y.toInt()});
    }
    return serializedPoints;
  }

  static List<Point<double>> _deserializePoints(List<Map<String, int>> points) {
    List<Point<double>> deserializedPoints = [];
    for (var pt in points) {
      deserializedPoints.add(Point(pt['x'].toDouble(), pt['y'].toDouble()));
    }
    return deserializedPoints;
  }
}

class HttpException with Exception {
  String message;
  HttpException(this.message);
}
