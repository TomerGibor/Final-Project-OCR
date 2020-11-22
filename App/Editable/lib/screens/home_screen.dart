import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'add_editable_screen.dart';
import '../widgets/editable_item.dart';
import '../widgets/app_drawer.dart';
import '../providers/editables.dart' show Editables;

class HomeScreen extends StatelessWidget {
  void _navigateToAddItemScreen(BuildContext context) {
    Navigator.of(context).pushNamed(AddEditableScreen.routeName).then((result) {
      if (result != null) {
        Provider.of<Editables>(context, listen: false).addEditable(result);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Your Editables'),
        actions: [
          IconButton(
            icon: Icon(Icons.add),
            onPressed: () => _navigateToAddItemScreen(context),
          )
        ],
      ),
      drawer: AppDrawer(),
      body: FutureBuilder(
        future: Provider.of<Editables>(context, listen: false)
            .fetchAndSetEditables(),
        builder: (ctx, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(
              child: const CircularProgressIndicator(),
            );
          } else {
            return Consumer<Editables>(
              child: const Center(
                child: const Text(
                  'You have no editables yet, start adding some!',
                  textAlign: TextAlign.center,
                ),
              ),
              builder: (ctx, editablesData, ch) {
                final editablesReversed = editablesData.items.reversed.toList();
                return editablesReversed.length == 0
                    ? ch
                    : ListView.builder(
                        itemBuilder: (ctx, i) {
                          return EditableItem(
                            editablesReversed[i].id,
                            editablesReversed[i].text,
                          );
                        },
                        itemCount: editablesReversed.length,
                      );
              },
            );
          }
        },
      ),
      floatingActionButton: FloatingActionButton(
        child: Icon(Icons.add),
        onPressed: () => _navigateToAddItemScreen(context),
      ),
    );
  }
}
