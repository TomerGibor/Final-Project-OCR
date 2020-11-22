import 'dart:io';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../widgets/image_input.dart';
import '../helpers/http_helper.dart';
import '../providers/settings.dart';
import '../widgets/error_dialog.dart';

class AddEditableScreen extends StatefulWidget {
  static const routeName = '/add-editable';

  @override
  _AddEditableScreenState createState() => _AddEditableScreenState();
}

class _AddEditableScreenState extends State<AddEditableScreen> {
  String _base64Image;
  var _isLoading = false;

  Future<void> _onImageSelected(File image) async {
    final bytes = await image.readAsBytes();
    setState(() {
      _base64Image = base64Encode(bytes);
    });
  }

  Future<void> _onSubmit() async {
    setState(() {
      _isLoading = true;
    });
    final preprocessing =
        Provider.of<Settings>(context, listen: false).preprocessing;
    try {
      final result =
          await HttpHelper.sendPostImageRequest(_base64Image, preprocessing);
      setState(() {
        _isLoading = false;
      });
      Navigator.of(context).pop(result);
    } catch (error) {
      showErrorAlertDialog(context).then((value) {
        setState(() {
          _isLoading = false;
        });
        Navigator.of(context).pop();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Editable'),
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          ImageInput(_onImageSelected, !_isLoading),
          _isLoading
              ? Column(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Padding(
                      padding: const EdgeInsets.all(20),
                      child: const Text('This might take a while...'),
                    ),
                    const CircularProgressIndicator(),
                  ],
                )
              : FlatButton.icon(
                  icon: Icon(Icons.send),
                  label: const Text('Submit'),
                  onPressed: _base64Image == null ? null : _onSubmit,
                ),
        ],
      ),
    );
  }
}
