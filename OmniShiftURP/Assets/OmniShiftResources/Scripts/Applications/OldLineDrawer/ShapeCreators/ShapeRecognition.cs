using System.Collections;
using System;
using System.Collections.Generic;
using UnityEngine;
using System.IO;

// needed for the Gesture etc.
using PDollarGestureRecognizer;

public class ShapeRecognition : MonoBehaviour
{

    // TODO
    // also implement a gesture add function. Not sure yet how to activate it though


    //public Transform lineRendererTrans;

    private List<Gesture> trainingSet = new List<Gesture>();

    //private List<Point> points = new List<Point>();
    //private int strokeId = -1;

   // private List<LineRenderer> gestureLinesRenderer = new List<LineRenderer>();
   // private LineRenderer currentGestureLineRenderer;

    //GUI
    public string recognitionString;
    private bool recognized;
    private string newGestureName = "";

    [Header("Own Variables")]
    [Tooltip("This should be the path to the xml files with the gesture sets")]
    public string gesturesFilePath;
    [Range(0.0f, 1.0f)]
    public float gestureRecognitionThreshold = 0.5f;


    /// <summary>
    /// Maybe put this into a different class altogether;
    /// </summary>
    //[Header("Gesture creation (Not yet implemented)")]
    //public bool createGesture;

    // Start is called before the first frame update
    void Start()
    {
        //Load pre-made gestures
        //TextAsset[] gesturesXml = Resources.LoadAll<TextAsset>("GestureSet/10-stylus-MEDIUM/");
        //foreach (TextAsset gestureXml in gesturesXml)
        //    trainingSet.Add(GestureIO.ReadGestureFromXML(gestureXml.text));

        //Load user custom gestures
        string[] filePaths = Directory.GetFiles(gesturesFilePath, "*.xml");
        foreach (string filePath in filePaths)
            trainingSet.Add(GestureIO.ReadGestureFromFile(filePath));
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    /// <summary>
    /// This checks upon the given points whether or not they form a known gesture. 
    /// If the score is above the threshold, a gesture will be given. Otherwise it will return "No gesture found".
    /// </summary>
    public string CheckForShape(List<Point> points)
    {
        Gesture candidate = new Gesture(points.ToArray());
        Result gestureResult = PointCloudRecognizer.Classify(candidate, trainingSet.ToArray());

        recognitionString = gestureResult.GestureClass + ":" + gestureResult.Score;


        if (gestureResult.Score > gestureRecognitionThreshold)
        {
            return recognitionString;//gestureResult.GestureClass;
        }
        else
        {
            return "No gesture found";
        }

    }

    /// <summary>
    /// Takes all the lines that contribute to the gesture and converts them to the Point list suited for the recognition. 
    /// It then returns the gesture if the threshold is above the recognition threshold. 
    /// Otherwise it will return "No gesture found".
    /// </summary>
    /// <param name="lines"></param>
    public string CheckForShape(List<LineRenderer> lines)
    {
        List<Point> pPoints = new List<Point>();

        int strokeId = 0;

        foreach(LineRenderer line in lines)
        {
            Vector3[] points = new Vector3[line.positionCount];
            line.GetPositions(points);

            for(int i = 0; i < points.Length; i++)
            {
                pPoints.Add(new Point(points[i].x, points[i].y, strokeId));
            }

            strokeId++;
        }


        return CheckForShape(pPoints);
    }
}
