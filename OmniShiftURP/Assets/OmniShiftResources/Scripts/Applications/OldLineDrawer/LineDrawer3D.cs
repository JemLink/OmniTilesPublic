using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LineDrawer3D : LineDrawer
{
    //[Header("Hand Representation")]
    //public Hand hand;
    public List<Vector3> fingerPositions;
    //public Hand.Gesture lastGesture = Hand.Gesture.Open;

    //[Header("Line Drawing")]

    //public GameObject linePrefab;

    //[Range(0.0f, 0.15f)]
    //public float lineWidth = 0.1f;
    //[Range(0.0f, 0.01f)]
    //public float minDrawingInterval = 0.001f;
    //public Color[] lineColors;
    //private int currentColorID = 0;

    //public Transform linesParent;
    //public GameObject currentLine;

    //public LineRenderer lineRenderer;

    // I will later see if there is a way to give colliders to 3D edges
    //public EdgeCollider2D edgeCollider;

    



    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void LateUpdate()
    {
        if (hand)
        {
            switch (hand.gesture)
            {
                case Hand.Gesture.Open:
                    // Change color for every opening

                    if (lastGesture != Hand.Gesture.Open)
                    {
                        currentColorID++;
                        currentColorID = currentColorID % lineColors.Length;
                    }

                    // check for shapes if line is finished
                    if (lastGesture == Hand.Gesture.Pointer)
                    {
                        lineController.TryRecognizingShape(currentLine);
                    }


                    lastGesture = Hand.Gesture.Open;

                    break;
                case Hand.Gesture.Closed:

                    // check for shapes if line is finished
                    if (lastGesture == Hand.Gesture.Pointer)
                    {
                        lineController.TryRecognizingShape(currentLine);
                    }

                    // later: eraze edges if possible
                    ErazeFullLine();
                    //ErazeLinePart();
                    lastGesture = Hand.Gesture.Closed;

                    break;
                case Hand.Gesture.Pointer:

                    if (lastGesture != Hand.Gesture.Pointer)
                    {
                        // we need the transform to get the world position
                        CreateLine(hand.jointsRep[8].transform.position);
                    }
                    else
                    {
                        
                        // index 8 is fingertip of index finger
                        Vector3 tmpFingerPos = hand.jointsRep[8].transform.position;

                        if (Vector3.Distance(tmpFingerPos, fingerPositions[fingerPositions.Count - 1]) > minDrawingInterval)
                        {
                            UpdateLine(tmpFingerPos);
                        }
                    }


                    lastGesture = Hand.Gesture.Pointer;

                    break;
                default:
                    Debug.Log("No Gesture detected: Something went wrong in switch case statement");
                    hand.gesture = lastGesture;
                    break;

            }

            

        }

        
        
    }





    



    void CreateLine(Vector3 fingerPos)
    {

        currentLine = Instantiate(linePrefab, transform.position, Quaternion.identity, lineController.linesParent);

        lineRenderer = currentLine.GetComponent<LineRenderer>();
        lineRenderer.material.color = lineColors[currentColorID];
        lineRenderer.widthMultiplier = lineWidth;
        //edgeCollider = currentLine.GetComponent<EdgeCollider2D>();

        // clear list
        fingerPositions.Clear();

        // add new finger position (need them twice since line renderer needs a start and an end point
        fingerPositions.Add(fingerPos);
        fingerPositions.Add(fingerPos);

        // set start and end point of line renderer
        lineRenderer.SetPosition(0, fingerPositions[0]);
        lineRenderer.SetPosition(1, fingerPositions[1]);

        //edgeCollider.points = fingerPositions.ToArray();
        lineController.AddLineToLines(currentLine);
    }

    void UpdateLine(Vector3 newFingerPos)
    {
        if (lineRenderer)
        {
            fingerPositions.Add(newFingerPos);

            lineRenderer.positionCount++;
            lineRenderer.SetPosition(lineRenderer.positionCount - 1, newFingerPos);
            //edgeCollider.points = fingerPositions.ToArray();
        }
    }








    #region erazing lines

    void ErazeFullLine()
    {
        // check which lines are contained in hand collider
        List<GameObject> linesToRemove = ReturnContainedLines(hand.handCollider);

        // delete line
        foreach (GameObject line in linesToRemove)
        {
            lineController.RemoveLineFromLines(line);
            Destroy(line);
        }
    }

    void ErazeLinePart()
    {
        ErazeContainedPoints(hand.handCollider);
    }


    public void ErazeContainedPoints(Collider col)
    {
        Vector3 colCenter = col.transform.InverseTransformPoint(col.bounds.center);
        Vector3 colExtents = col.bounds.extents;

        //List<GameObject> linesToRemove = new List<GameObject>();
        Dictionary<GameObject, List<int>> linesWithPointsToRemove = new Dictionary<GameObject, List<int>>();

        foreach (GameObject line in lineController.GetLines())
        {
            List<int> containedPointsID = new List<int>();

            Vector3[] linePositions = new Vector3[line.GetComponent<LineRenderer>().positionCount];

            line.GetComponent<LineRenderer>().GetPositions(linePositions);


            for(int i = 0; i < linePositions.Length; i++)
            {
                // find contained points

                if (PointContained(colCenter, colExtents, linePositions[i]))
                {
                    containedPointsID.Add(i);
                    
                    
                }
            }

            if(containedPointsID.Count > 0)
            {
                linesWithPointsToRemove.Add(line, containedPointsID);
            }
            

            

            
        }

        foreach(GameObject line in linesWithPointsToRemove.Keys)
        {
            // eraze contained points and split line

            LineRenderer lr = line.GetComponent<LineRenderer>();
            SplitLine(lr, linesWithPointsToRemove[line]);

            lineController.RemoveLineFromLines(line);
            Destroy(line);
        }

        
    }


    /// <summary>
    /// Splits the line and deletes the points with the IDsToEraze.
    /// If there is no IDs in the list the function does nothing
    /// </summary>
    /// <param name="lr"></param>
    /// <param name="IDsToEraze"></param>
    private void SplitLine(LineRenderer lr, List<int> IDsToEraze)
    {
        if(IDsToEraze.Count > 0)
        {
            // split line and add the new lines to lines

            bool newLine = true;


            for (int i = 0; i < lr.positionCount; i++)
            {
                if (!IDsToEraze.Contains(i))
                {
                    if (newLine)
                    {
                        CreateLine(lr.GetPosition(i));
                        newLine = false;
                    }
                    else
                    {
                        UpdateLine(lr.GetPosition(i));
                    }
                }
                else
                {
                    newLine = true;
                }

            }
        }

        

    }



    public List<GameObject> ReturnContainedLines(Collider col)
    {
        Vector3 colCenter = col.transform.InverseTransformPoint(col.bounds.center);
        Vector3 colExtents = col.bounds.extents;

        List<GameObject> containedLines = new List<GameObject>();

        foreach (GameObject line in lineController.GetLines())
        {
            Vector3[] linePositions = new Vector3[line.GetComponent<LineRenderer>().positionCount];

            line.GetComponent<LineRenderer>().GetPositions(linePositions);
            
            foreach (Vector3 point in linePositions)
            {
                //Vector3 localPoint = lineController.linesParent.InverseTransformPoint(point);

                if (PointContained(colCenter, colExtents, point))
                {
                    containedLines.Add(line);
                    break;
                }

            }
        }


        return containedLines;
    }


    /// <summary>
    /// Checks if the point is contained within the desginated field
    /// </summary>
    /// <param name="center"></param>
    /// <param name="extents"></param>
    /// <param name="point"></param>
    /// <returns></returns>
    private bool PointContained(Vector2 center, Vector2 extents, Vector2 point)
    {
        //Vector3 localPoint = transform.InverseTransformPoint(point);

        Debug.Log("Center " + center);
        Debug.Log("extends " + extents);
        Debug.Log("Point " + point);
        //Debug.Log("local Point " + localPoint);
        
        bool containsX = ((center.x - extents.x) < point.x) && ((center.x + extents.x) > point.x);
        bool containsY = ((center.y - extents.y) < point.y) && ((center.y + extents.y) > point.y);


        if (containsX && containsY)
        {
            return true;
        }
        else
        {
            return false;
        }
    }

    /// <summary>
    /// Checks if the 2D point is contained in the projection of the 3D field. 
    /// So only x and y will be checked while z is discarded.
    /// </summary>
    /// <param name="center"></param>
    /// <param name="extents"></param>
    /// <param name="point"></param>
    /// <returns></returns>
    private bool PointContained(Vector2 center, Vector2 extents, Vector3 point)
    {
        Vector3 localPoint = lineController.linesParent.InverseTransformPoint(point);
        //Vector3 localPoint = transform.InverseTransformPoint(point);

        //Debug.Log("Center " + center.x + ", " + center.y);
        //Debug.Log("extends " + extents.x + ", " + extents.y);
        //Debug.Log("Point " + point.x + ", " + point.y);
        //Debug.Log("local Point " + localPoint.x + ", " + localPoint.y);

        bool containsX = ((center.x - extents.x) < localPoint.x) && ((center.x + extents.x) > localPoint.x);
        bool containsY = ((center.y - extents.y) < localPoint.y) && ((center.y + extents.y) > localPoint.y);

        //Debug.Log("contains x " + containsX);
        //Debug.Log("contains y " + containsY);


        if (containsX && containsY)
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    


    #endregion

}
