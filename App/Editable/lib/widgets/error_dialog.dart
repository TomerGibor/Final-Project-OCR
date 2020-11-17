import 'package:flutter/material.dart';

Future<void> showErrorAlertDialog(BuildContext context) {
  return showDialog(
    context: context,
    builder: (_) => new AlertDialog(
      title: new Text('Unexpected error!'),
      content:
          new Text('An Unexpected Error has Occurred. Please try again later.'),
      actions: <Widget>[
        FlatButton(
          child: Text('OK'),
          onPressed: () {
            Navigator.of(context).pop();
          },
        )
      ],
    ),
  );
}
