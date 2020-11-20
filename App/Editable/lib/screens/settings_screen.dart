import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../widgets/app_drawer.dart';
import '../providers/settings.dart';

class SettingsScreen extends StatefulWidget {
  static const routeName = '/settings';

  @override
  _SettingsScreenState createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  var _preprocess = false;

  Widget _buildSwitchListTile(
    String title,
    String description,
    bool value,
    Function updateValue,
  ) {
    return SwitchListTile(
      title: Text(title),
      value: value,
      subtitle: Text(
        description,
      ),
      onChanged: updateValue,
    );
  }

  Future<void> initializeData() async {
    final settingsProvider = Provider.of<Settings>(context, listen: false);
    await settingsProvider.fetchAndSetSettings();
    _preprocess = await settingsProvider.preprocessing;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: AppDrawer(),
      appBar: AppBar(
        title: Text('Settings'),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(20),
            child: Text(
              'Adjust your app settings',
              style: Theme.of(context).textTheme.headline6,
            ),
          ),
          FutureBuilder(
            future: initializeData(),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return Center(
                  child: CircularProgressIndicator(),
                );
              }
              return Expanded(
                child: ListView(
                  children: [
                    _buildSwitchListTile(
                      'Preprocessing',
                      'Pre-process image before performing the text extraction',
                      _preprocess,
                      (newValue) {
                        Provider.of<Settings>(context, listen: false)
                            .setPreprocessing(newValue);
                        setState(() {
                          _preprocess = newValue;
                        });
                      },
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
