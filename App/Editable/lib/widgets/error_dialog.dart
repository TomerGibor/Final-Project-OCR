import 'package:flutter/material.dart';

Future<void> showErrorAlertDialog(BuildContext context) {
  return showDialog(
    context: context,
    builder: (_) => new AlertDialog(
      title: new Text('Unexpected Error!'),
      content:
          new Text('An unexpected error has occurred. Please try again later.'),
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
