import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import 'screens/home_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/add_editable_screen.dart';
import 'screens/edit_editable_screen.dart';
import 'providers/editables.dart';
import 'providers/settings.dart';

void main() => runApp(App());

class App extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);

    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (ctx) => Settings(),
        ),
        ChangeNotifierProvider(
          create: (ctx) => Editables(),
        ),
      ],
      child: Consumer<Settings>(
        builder: (ctx, settings, child) => MaterialApp(
          theme: ThemeData(
            primarySwatch: Colors.indigo,
            accentColor: Colors.deepOrange,
            visualDensity: VisualDensity.adaptivePlatformDensity,
            textTheme: Theme.of(context).textTheme.apply(
                  fontSizeFactor: settings.fontSizeFactor,
                ),
            brightness: settings.darkTheme ? Brightness.dark : Brightness.light,
          ),
          home: HomeScreen(),
          routes: {
            SettingsScreen.routeName: (ctx) => SettingsScreen(),
            AddEditableScreen.routeName: (ctx) => AddEditableScreen(),
            EditEditableScreen.routeName: (ctx) => EditEditableScreen(),
          },
          debugShowCheckedModeBanner: false,
        ),
      ),
    );
  }
}
