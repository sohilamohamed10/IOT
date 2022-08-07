// ignore_for_file: avoid_print, prefer_typing_uninitialized_variables, non_constant_identifier_names, prefer_const_constructors

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:blinking_point/blinking_point.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    // Replace with actual values
    options: const FirebaseOptions(
      apiKey: "AIzaSyDn9fY_ZqLynD0Y0osSXuYLGYNvQRjZ4rU",
      authDomain: "https://task1fire-default-rtdb.firebaseio.com",
      databaseURL: "https://task1fire-default-rtdb.firebaseio.com",
      appId: "1:650912343113:android:6d21f80c7e4d62e250cb98",
      messagingSenderId: "650912343113",
      projectId: "task1fire",
    ),
  );
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key key}) : super(key: key);

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Indoor_Localizer',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.deepOrange,
      ),
      home: const MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({Key key}) : super(key: key);

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Timer timer;
  // List<int> label_list = [];
  List<double> btm_list = [];
  List<double> rt_list = [];
  double btm = 0;
  double rt = 0;
  double r_btm = 0;
  double r_rt = 0;
  int label;
  int dublicate_label = 9;
  final dbRef = FirebaseDatabase.instance.ref();
  int counter = 0;
  bool value = false;
  int index = 0;

  @override
  void initState() {
    super.initState();
  }

  void _replay(Timer timer) {
    setState(() {
      if (index < btm_list.length) {
        index++;
        if (index == btm_list.length) {
          index = 0;
        }
        print(index);
      }
    });
  }

  void _Showpoint() {
    setState(() {
      value = !value;
      if (value) {
        timer = Timer.periodic(const Duration(milliseconds: 5000), _replay);
      }
    });
  }

  void _update() {
    if (label == 0) {
      //Lec hall
      btm = 500;
      rt = 280;
      r_btm = 450;
      r_rt = 350;
      // print(label);
    } else if (label == 1) {
      // hallway1
      btm = 450;
      rt = 350;
      r_btm = 350;
      r_rt = 400;
      // print(label);
    } else if (label == 2) {
      //hallway3
      btm = 300;
      rt = 350;
      r_btm = 370;
      r_rt = 700;
      // print(label);
    } else if (label == 3) {
      //elecLab1
      btm = 230;
      rt = 400;
      r_btm = 260;
      r_rt = 880;
      // print(label);
    }
    if (btm_list.length < 51) {
      if (dublicate_label != label) {
        dublicate_label = label;
        btm_list.add(r_btm);
        rt_list.add(r_rt);
      }
      // counter++;
      print(btm_list);
      print(rt_list);
      print(btm_list.length);
    } else {
      // counter = 0;
      btm_list.removeAt(0);
      rt_list.removeAt(0);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SBME_Locallizer'),
        backgroundColor: Colors.deepOrange,
        centerTitle: true,
      ),
      body: StreamBuilder(
          stream: dbRef.child('label').onValue,
          builder: (context, snapshot) {
            Widget imagewidget;
            if (snapshot.hasData &&
                !snapshot.hasError &&
                snapshot.data.snapshot.value != null) {
              label = snapshot.data.snapshot.value;
              print("label");
              print(label);
              _update();
              imagewidget = Center(
                child: Stack(
                  children: <Widget>[
                    Container(
                        width: 720,
                        height: 1280,
                        decoration: const BoxDecoration(
                          image: DecorationImage(
                              image: AssetImage("images/SBME_Map.jpg")),
                        ),
                        child: value
                            ? BlinkingPoint(
                                xCoor: btm_list[index],
                                yCoor: rt_list[index],
                                pointColor: Colors.green,
                                pointSize: 5.0,
                              )
                            : null),
                    Positioned(
                        bottom: btm,
                        right: rt,
                        child: const Icon(Icons.location_on,
                            color: Colors.deepOrange)),
                  ],
                ),
              );
            } else {
              // return Text('State: ${snapshot.connectionState}');
              imagewidget = const Center(child: CircularProgressIndicator());
            }
            return imagewidget;
          }),
      floatingActionButton: FloatingActionButton(
        onPressed: _Showpoint,
        tooltip: 'Replay',
        child: Icon(Icons.replay),
      ),
    );
  }
}

// if (label == 0) {
//       //Lec hall
//       btm = 600;
//       rt = 150;
//       r_btm = 250;
//       r_rt = 350;
//       // print(label);
//     } else if (label == 1) {
//       // hallway1
//       btm = 500;
//       rt = 180;
//       r_btm = 200;
//       r_rt = 500;
//       // print(label);
//     } else if (label == 2) {
//       //hallway3
//       btm = 320;
//       rt = 180;
//       r_btm = 200;
//       r_rt = 900;
//       // print(label);
//     } else if (label == 3) {
//       //elecLab1
//       btm = 270;
//       rt = 250;
//       r_btm = 100;
//       r_rt = 1000;
//       // print(label);
//     }