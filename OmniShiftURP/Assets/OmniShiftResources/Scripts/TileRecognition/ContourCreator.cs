using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ContourCreator : MonoBehaviour
{

    [Header("Shape Recognition")]
    public ShapeRecognition shapeRecognizer;
    [Tooltip("This is the size of the image from opencv (usually 800x800 or 400x400")]
    public Vector2 imageSize;
    public float scale;


    [Header("Line handling")]
    public GameObject linePrefab;
    public Transform linesParent;

    LineRenderer lines;



    [Header("Tiles Handler")]
    public TilesHandler tilesHandler;


    public class LineObj
    {
        public List<LineRenderer> line;
        public Vector3[] vertices;
        public Vector3 center;
        public float area;
    }
    


    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void CreateContours(string contourString)
    {
        // split string into single contours
        string[] contours = contourString.Split('c');

        // start from 1 since the string before c is empty
        for(int i = 1; i < contours.Length; i++)
        {
            CreateSingleContour(contours[i]);
        }

        // create lines according to coordinates

        // detect shape of contour via ShapeRecognition.CheckForShape

    }

    private void CreateSingleContour(string contour)
    {
        LineObj line = CreateLineObjFromString(contour);

        if (line == null)
        {
            return;
        }

        // this returns the message in the form: detectedContour:score
        string detectedContour = shapeRecognizer.CheckForShape(line.line);
        
        string[] detectedContourWithScore = detectedContour.Split(':');

        switch (detectedContourWithScore[0])
        {
            case "Triangle":
                Debug.Log("Should create triangle: " + detectedContourWithScore[1]);
                tilesHandler.CreateTriangle(line.area, line.center, line.vertices);
                break;
            case "Square":
                Debug.Log("Should create square" + detectedContourWithScore[1]);
                tilesHandler.CreateSquare(line.area, line.center, line.vertices);
                break;
            case "Pentagon":
                Debug.Log("Should create pentagon" + detectedContourWithScore[1]);
                tilesHandler.CreatePentagon(line.area, line.center, line.vertices);
                break;
            default:
                Debug.Log("No shape detected: " + detectedContourWithScore[0]);
                break;
        }
    }

    private LineObj CreateLineObjFromString(string contourString)
    {
        Debug.Log("Should create line object");
        float area = 0;
        Vector3 center = Vector3.zero;
        string verticesStr = "";

        SplitIntoLineObjComponents(contourString, out area, out center, out verticesStr);

        // contour string should have the form of x,y;x,y;...
        string[] verticesStrings = verticesStr.Split(';');


        // if vertices are two small: skip this line
        if(verticesStrings.Length < 3) // 3 would be triangle, so our minimum shape
        {
            Debug.Log("Not enough vertices for line");
            return null;
        }



        GameObject lineObj = Instantiate(linePrefab, Vector3.zero, Quaternion.identity, linesParent);
        LineRenderer line = lineObj.GetComponent<LineRenderer>();
        Vector3[] vertices = new Vector3[verticesStrings.Length];

        // only until length - 1 since last split is empty
        for (int i = 0; i < verticesStrings.Length - 1; i++)
        {
            //Debug.Log("Vertice: " + vertices[i]);
            string[] xy = verticesStrings[i].Split(',');
            float x = float.Parse(xy[0]);
            float y = float.Parse(xy[1]);

            if(i >= line.positionCount)
            {
                line.positionCount++;
            }

            vertices[i] = ConvertFromOpenCVToUnitySpace(new Vector3(x, y, 0));
            line.SetPosition(i, ConvertFromOpenCVToUnitySpace(new Vector3(x,y,0)));
            // add center(middle) later as well
                        
        }

        // make sure first and last vertex are the same since we are looking for closed contours
        line.positionCount++;
        line.SetPosition(line.positionCount - 1, line.GetPosition(0));

        // convert it to lineRenderer list for the shape recognition
        List<LineRenderer> returnLine = new List<LineRenderer>();
        returnLine.Add(line);

        LineObj returnCont = new LineObj();
        returnCont.line = returnLine;
        returnCont.vertices = vertices;
        returnCont.area = area;
        returnCont.center = center;

        return returnCont;

    }


    


    private void SplitIntoLineObjComponents(string contourString, out float area, out Vector3 center, out string verticesStr)
    {
        // first split it into area, center(middle) and vertices
        // should have some form like: axmx,yvx,y;x,y;...

        // split into vertices etc.
        string[] tmpStr = contourString.Split('v');
        // [0] should be the part with area and center, so we need index 1 for vertices
        verticesStr = tmpStr[1];


        // get center
        // the [0] should be the area string before m
        tmpStr = tmpStr[0].Split('m');
        string centerStr = tmpStr[1];
        string[] xy = centerStr.Split(',');
        float x = float.Parse(xy[0]);
        float y = float.Parse(xy[1]);
        center = ConvertFromOpenCVToUnitySpace(new Vector3(x, y, 0));


        // get area
        // the [0] should be the empty string before a
        string areaStr = tmpStr[0].Split('a')[1];
        area = float.Parse(areaStr);
    }


    #region Helper functions

    private Vector3 ConvertFromOpenCVToUnitySpace(Vector3 openCVCoords)
    {
        //Debug.Log("open cv: " + openCVCoords);

        // map to range of 0 to 1
        float x = openCVCoords.x / imageSize.x;
        float y = openCVCoords.y / imageSize.y;

        // map of range from -1 to 1
        x = -(x * 2.0f) + 1; // x must be flipped since opencv has different handed coordinate system
        y = (y * 2.0f) - 1;


        return new Vector3(x, y, openCVCoords.z) * scale;

    }

    #endregion
}
