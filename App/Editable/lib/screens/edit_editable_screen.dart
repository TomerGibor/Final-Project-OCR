import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/editables.dart';

class EditEditableScreen extends StatefulWidget {
  static const routeName = '/edit-editable';

  @override
  _EditEditableScreenState createState() => _EditEditableScreenState();
}

class _EditEditableScreenState extends State<EditEditableScreen> {
  final _controller = TextEditingController();
  String _editableId;
  var _valid = true;

  @override
  void initState() {
    super.initState();
    Future.delayed(Duration.zero).then((_) {
      _editableId = ModalRoute.of(context).settings.arguments as String;
      _controller.text = Provider.of<Editables>(context, listen: false)
          .getById(_editableId)
          .text;
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Edit Editable'),
        actions: [
          IconButton(
              icon: Icon(Icons.save),
              onPressed: () {
                setState(() {
                  _controller.text.isEmpty ? _valid = false : _valid = true;
                });
                if (!_valid) {
                  return;
                }
                Provider.of<Editables>(context, listen: false)
                    .setTextById(_editableId, _controller.text);
                Navigator.of(context).pop();
              }),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: TextField(
          decoration: InputDecoration(
            labelText: 'Editable Text',
            errorText: !_valid ? "Value Can't Be Empty" : null,
          ),
          maxLines: 20,
          style: TextStyle(
            fontSize: 18,
          ),
          controller: _controller,
        ),
      ),
    );
  }
}
