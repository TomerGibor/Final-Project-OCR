import 'dart:io';
import 'dart:math';

import 'package:flutter/material.dart';

class SelectPointsOnImageScreen extends StatefulWidget {
  final File imageFile;
  final List<Point<double>> points;
  final int imgWidth, imgHeight;

  const SelectPointsOnImageScreen(
    this.imageFile,
    this.points, {
    @required this.imgWidth,
    @required this.imgHeight,
  });

  @override
  _SelectPointsOnImageScreenState createState() =>
      _SelectPointsOnImageScreenState();
}

class _SelectPointsOnImageScreenState extends State<SelectPointsOnImageScreen> {
  static const PADDING = 30.0;
  static const PT_RADIUS = 8.0;
  final _stackKey = GlobalKey();
  double _imgWidthOnScreen, _imgHeightOnScreen;
  double _scale;
  bool _initDone = false;
  int _currentlyDraggedIndex = -1;
  List<Point<double>> _modifiedPoints = [];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_initDone) {
      final width = MediaQuery.of(context).size.width;
      _imgWidthOnScreen = width - PADDING * 2;
      _scale = _imgWidthOnScreen / widget.imgWidth;
      _imgHeightOnScreen = widget.imgHeight * _scale;
      _modifiedPoints = [...widget.points];
      _initDone = true;
    }
  }

  Widget _buildPositionedPoint(int indexInPoints) {
    final pt = _modifiedPoints[indexInPoints];
    return Positioned(
      left: pt.x * _scale - PT_RADIUS,
      top: pt.y * _scale - PT_RADIUS,
      child: CircleAvatar(
        radius: PT_RADIUS,
        backgroundColor: Theme.of(context).accentColor.withOpacity(0.7),
      ),
    );
  }

  Point<double> _translatePoint(double x, double y) {
    final newX = (x - _stackKey.globalPaintBounds.left) / _scale;
    final newY = (y - _stackKey.globalPaintBounds.top) / _scale;
    return Point(newX, newY);
  }

  List<Offset> get _offsets {
    List<Offset> offsets = [];
    for (var pt in _modifiedPoints) {
      final newX = pt.x * _scale;
      final newY = pt.y * _scale;
      offsets.add(Offset(newX, newY));
    }
    return offsets;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Select points'),
      ),
      body: Padding(
        padding: EdgeInsets.symmetric(horizontal: PADDING),
        child: GestureDetector(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              Center(
                child: Stack(
                  key: _stackKey,
                  overflow: Overflow.visible,
                  children: [
                    Image.file(widget.imageFile),
                    for (int i = 0; i < _modifiedPoints.length; i++)
                      _buildPositionedPoint(i),
                    CustomPaint(
                      painter:
                          LinesPainter(_offsets, Theme.of(context).accentColor),
                    ),
                  ],
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  FlatButton(
                    child: Text('Cancel'),
                    onPressed: () {
                      Navigator.of(context).pop();
                    },
                  ),
                  FlatButton(
                    child: Text('Reset'),
                    onPressed: () {
                      setState(() {
                        _modifiedPoints = [...widget.points];
                      });
                    },
                  ),
                  FlatButton(
                    child: Text('Confirm'),
                    onPressed: () {
                      Navigator.of(context).pop(_modifiedPoints);
                    },
                  ),
                ],
              )
            ],
          ),
          onPanStart: (dragStartDetails) {
            var indexMatch = -1;
            final pt = _translatePoint(dragStartDetails.globalPosition.dx,
                dragStartDetails.globalPosition.dy);
            for (var i = 0; i < _modifiedPoints.length; i++) {
              final distance = sqrt(pow(pt.x - _modifiedPoints[i].x, 2) +
                  pow(pt.y - _modifiedPoints[i].y, 2));
              if (distance <= widget.imgHeight / 5) {
                indexMatch = i;
                break;
              }
            }
            if (indexMatch != -1) {
              _currentlyDraggedIndex = indexMatch;
            }
          },
          onPanUpdate: (dragUpdateDetails) {
            if (_currentlyDraggedIndex != -1) {
              final pt = _translatePoint(dragUpdateDetails.globalPosition.dx,
                  dragUpdateDetails.globalPosition.dy);
              double x = pt.x;
              double y = pt.y;
              if (x < 0)
                x = 0;
              else if (x > widget.imgWidth) x = widget.imgWidth.toDouble();
              if (y < 0)
                y = 0;
              else if (y > widget.imgHeight) y = widget.imgHeight.toDouble();

              setState(() {
                _modifiedPoints[_currentlyDraggedIndex] = Point(x, y);
              });
            }
          },
          onPanEnd: (_) {
            setState(() {
              _currentlyDraggedIndex = -1;
            });
          },
        ),
      ),
    );
  }
}

extension GlobalKeyExtension on GlobalKey {
  Rect get globalPaintBounds {
    final renderObject = currentContext?.findRenderObject();
    var translation = renderObject?.getTransformTo(null)?.getTranslation();
    if (translation != null && renderObject.paintBounds != null) {
      return renderObject.paintBounds
          .shift(Offset(translation.x, translation.y));
    } else {
      return null;
    }
  }
}

class LinesPainter extends CustomPainter {
  final List<Offset> offsets;
  final Color lineColor;

  LinesPainter(this.offsets, this.lineColor);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = lineColor.withOpacity(0.9)
      ..strokeCap = StrokeCap.square
      ..style = PaintingStyle.fill
      ..strokeWidth = 2;

    for (int i = 0; i < offsets.length; i++) {
      if (i + 1 == offsets.length) {
        canvas.drawLine(offsets[i], offsets[0], paint);
      } else {
        canvas.drawLine(offsets[i], offsets[i + 1], paint);
      }
    }
  }

  @override
  bool shouldRepaint(LinesPainter oldPainter) => oldPainter.offsets != offsets;
}
