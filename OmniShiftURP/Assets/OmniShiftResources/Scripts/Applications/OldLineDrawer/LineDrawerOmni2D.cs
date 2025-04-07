using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LineDrawerOmni2D : LineDrawer
{
    //[Header("Hand Representation")]
    //public Hand hand;
    public List<Vector2> fingerPositions;
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

    //// I will later see if there is a way to give colliders to 3D edges
    public EdgeCollider2D edgeCollider;





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


                    lastGesture = Hand.Gesture.Open;

                    break;
                case Hand.Gesture.Closed:
                    // later: eraze edges if possible
                    ErazeFullLine();
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
                        Vector2 tmpFingerPos = hand.jointsRep[8].transform.position;

                        if (Vector2.Distance(tmpFingerPos, fingerPositions[fingerPositions.Count - 1]) > minDrawingInterval)
                        {
                            UpdateLine(tmpFingerPos);
                        }
                    }


                    lastGesture = Hand.Gesture.Pointer;

                    break;
                default:
                    Debug.Log("No Gesture detected: Something went wrong in switch case statement");
                    break;

            }
        }



    }









    void CreateLine(Vector2 fingerPos)
    {

        currentLine = Instantiate(linePrefab, transform.position, Quaternion.identity, lineController.linesParent);

        lineRenderer = currentLine.GetComponent<LineRenderer>();
        lineRenderer.material.color = lineColors[currentColorID];
        lineRenderer.widthMultiplier = lineWidth;
        edgeCollider = currentLine.GetComponent<EdgeCollider2D>();

        // clear list
        fingerPositions.Clear();

        // add new finger position (need them twice since line renderer needs a start and an end point
        fingerPositions.Add(fingerPos);
        fingerPositions.Add(fingerPos);

        // set start and end point of line renderer
        lineRenderer.SetPosition(0, fingerPositions[0]);
        lineRenderer.SetPosition(1, fingerPositions[1]);

        edgeCollider.points = fingerPositions.ToArray();

        lineController.AddLineToLines(currentLine);
    }

    void UpdateLine(Vector3 newFingerPos)
    {
        fingerPositions.Add(newFingerPos);

        lineRenderer.positionCount++;
        lineRenderer.SetPosition(lineRenderer.positionCount - 1, newFingerPos);

        edgeCollider.points = fingerPositions.ToArray();
    }



    void ErazeFullLine()
    {
        // check which lines are contained in hand collider
        List<GameObject> linesToRemove = ReturnContainedLines(hand.handCollider);

        // delete line
        foreach(GameObject line in linesToRemove)
        {
            lineController.RemoveLineFromLines(line);
            Destroy(line);
        }
    }

    void ErazeLinePart()
    {
        // check if line is within hand collider

        // split the line into two and eraze middle part
    }





    public List<GameObject> ReturnContainedLines (Collider col)
    {
        Vector3 colCenter = col.transform.InverseTransformPoint(col.bounds.center);
        Vector3 colExtents = col.bounds.extents;

        List<GameObject> containedLines = new List<GameObject>();

        foreach(GameObject line in lineController.GetLines())
        {
            Vector2[] points = GetComponent<EdgeCollider2D>().points;

            foreach(Vector2 point in points)
            {
                if(PointContained(colCenter, colExtents, point))
                {
                    containedLines.Add(line);
                    break;
                }
                
            }
        }


        return containedLines;
    }


    private bool PointContained(Vector2 center, Vector2 extents, Vector2 point)
    {
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


    public bool ColliderContains(Collider col, Vector2 point)
    {
        Vector3 colCenter = col.transform.InverseTransformPoint(col.bounds.center);
        Vector3 colExtents = col.bounds.extents;

        bool containsX = ((colCenter.x - colExtents.x) < point.x) && ((colCenter.x + colExtents.x) > point.x);
        bool containsY = ((colCenter.y - colExtents.y) < point.y) && ((colCenter.y + colExtents.y) > point.y);


        if (containsX && containsY)
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    


    public bool ColliderContains(Collider col, Vector3 point)
    {
        Vector3 colCenter = col.transform.InverseTransformPoint(col.bounds.center);
        Vector3 colExtents = col.bounds.extents;

        bool containsX = ((colCenter.x - colExtents.x) < point.x) && ((colCenter.x + colExtents.x) > point.x);
        bool containsY = ((colCenter.y - colExtents.y) < point.y) && ((colCenter.y + colExtents.y) > point.y);
        bool containsZ = ((colCenter.z - colExtents.z) < point.z) && ((colCenter.z + colExtents.z) > point.z);


        if (containsX && containsY && containsZ)
        {
            return true;
        }
        else
        {
            return false;
        }
    }
}
