import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:share/share.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../providers/editables.dart';
import '../screens/edit_editable_screen.dart';
import 'error_dialog.dart';

class EditableItem extends StatelessWidget {
  final String id;
  final String text;

  EditableItem(this.id, this.text);

  Future<void> _launchTranslateInBrowser(BuildContext context) async {
    final url =
        'https://translate.google.com/#view=home&op=translate&sl=en&tl=iw&text=$text';

    if (await canLaunch(url)) {
      await launch(
        url,
        forceSafariVC: false,
        forceWebView: false,
        enableJavaScript: true,
      );
    } else {
      showErrorAlertDialog(context);
    }
  }

  void _copyToClipboard(BuildContext context) {
    Clipboard.setData(ClipboardData(text: text)).then((_) {
      Scaffold.of(context).hideCurrentSnackBar();
      Scaffold.of(context).showSnackBar(
        SnackBar(
          content: const Text('Copied to Clipboard'),
          duration: const Duration(seconds: 2),
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Dismissible(
      key: ValueKey(id),
      background: Container(
        color: Theme.of(context).errorColor,
        child: Icon(
          Icons.delete,
          color: Colors.white54,
          size: 40,
        ),
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        margin: const EdgeInsets.symmetric(
          horizontal: 15,
          vertical: 4,
        ),
      ),
      direction: DismissDirection.endToStart,
      confirmDismiss: (direction) {
        return showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Are you sure?'),
            content: const Text(
              'Do you want to remove the item?',
            ),
            actions: <Widget>[
              FlatButton(
                child: const Text('No'),
                onPressed: () {
                  Navigator.of(ctx).pop(false);
                },
              ),
              FlatButton(
                child: const Text('Yes'),
                onPressed: () {
                  Navigator.of(ctx).pop(true);
                },
              ),
            ],
          ),
        );
      },
      onDismissed: (direction) {
        Provider.of<Editables>(context, listen: false).removeById(id);
      },
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: Card(
          margin: const EdgeInsets.all(8),
          elevation: 5,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    text,
                    style: TextStyle(
                      fontSize:
                          Theme.of(context).textTheme.headline6.fontSize * 0.8,
                    ),
                  ),
                ),
              ),
              Column(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  IconButton(
                    icon: Icon(
                      Icons.translate,
                      color: Theme.of(context).primaryColor,
                    ),
                    onPressed: () async {
                      await _launchTranslateInBrowser(context);
                    },
                  ),
                  IconButton(
                    icon: Icon(
                      Icons.edit,
                      color: Theme.of(context).primaryColor,
                    ),
                    onPressed: () {
                      Navigator.of(context).pushNamed(
                          EditEditableScreen.routeName,
                          arguments: id);
                    },
                  ),
                ],
              ),
              Column(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  IconButton(
                    icon: Icon(
                      Icons.copy,
                      color: Theme.of(context).primaryColor,
                    ),
                    onPressed: () => _copyToClipboard(context),
                  ),
                  IconButton(
                    icon: Icon(
                      Icons.share,
                      color: Theme.of(context).primaryColor,
                    ),
                    onPressed: () {
                      Share.share(text);
                    },
                  ),
                  IconButton(
                    icon: ImageIcon(
                      AssetImage('assets/images/docx_icon.png'),
                      color: Theme.of(context).primaryColor,
                    ),
                    onPressed: () {},
                  ),
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}
