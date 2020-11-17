import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class ImageInput extends StatefulWidget {
  final Function onImageSelected;
  final bool showButtons;

  ImageInput(this.onImageSelected, [this.showButtons = true]);

  @override
  _ImageInputState createState() => _ImageInputState();
}

class _ImageInputState extends State<ImageInput> {
  File _image;
  final _imagePicker = ImagePicker();

  Future<void> _getImage(ImageSource imgSource) async {
    final pickedFile = await _imagePicker.getImage(source: imgSource);

    if (pickedFile == null) {
      return;
    }

    setState(() {
      _image = File(pickedFile.path);
    });

    widget.onImageSelected(_image);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Container(
          width: double.infinity,
          height: 400,
          child: _image != null
              ? Image.file(
                  _image,
                  fit: BoxFit.cover,
                  width: double.infinity,
                )
              : Text(
                  'No Image Selected!',
                  textAlign: TextAlign.center,
                ),
          alignment: Alignment.center,
        ),
        SizedBox(height: 10),
        if (widget.showButtons)
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              FlatButton.icon(
                icon: Icon(Icons.camera_alt),
                label: Text('Take Picture'),
                onPressed: () => _getImage(ImageSource.camera),
              ),
              FlatButton.icon(
                icon: Icon(Icons.image),
                label: Text('Select From Gallery'),
                onPressed: () => _getImage(ImageSource.gallery),
              )
            ],
          )
      ],
    );
  }
}
