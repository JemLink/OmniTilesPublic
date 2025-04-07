using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LineDrawer2D : MonoBehaviour
{
    public GameObject linePrefab;
    public Transform linesParent;
    public GameObject currentLine;

    public LineRenderer lineRenderer;
    public EdgeCollider2D edgeCollider;

    // see later if I can change this to 3D
    public List<Vector2> fingerPositions;

    public ShapeCreator testShapeCreator;


    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetMouseButtonDown(0))
        {
            CreateLine();
        }

        if (Input.GetMouseButton(0))
        {
            Vector2 tmpFingerPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);

            if (Vector2.Distance(tmpFingerPos, fingerPositions[fingerPositions.Count - 1]) > 0.1f)
            {
                UpdateLine(tmpFingerPos);
            }

        }

        if (Input.GetMouseButtonUp(0))
        {
            Vector3[] points = new Vector3[currentLine.GetComponent<LineRenderer>().positionCount];
            currentLine.GetComponent<LineRenderer>().GetPositions(points);

            testShapeCreator.CreateShape(currentLine.GetComponent<LineRenderer>());
        }
    }

    void CreateLine()
    {

        currentLine = Instantiate(linePrefab, Vector3.zero, Quaternion.identity, linesParent);
        
        lineRenderer = currentLine.GetComponent<LineRenderer>();
        edgeCollider = currentLine.GetComponent<EdgeCollider2D>();

        // clear list
        fingerPositions.Clear();

        // add new finger position (need them twice since line renderer needs a start and an end point
        fingerPositions.Add(Camera.main.ScreenToWorldPoint(Input.mousePosition));
        fingerPositions.Add(Camera.main.ScreenToWorldPoint(Input.mousePosition));

        // set start and end point of line renderer
        lineRenderer.SetPosition(0, fingerPositions[0]);
        lineRenderer.SetPosition(1, fingerPositions[1]);

        edgeCollider.points = fingerPositions.ToArray();
    }

    void UpdateLine(Vector2 newFingerPos)
    {
        fingerPositions.Add(newFingerPos);

        lineRenderer.positionCount++;
        lineRenderer.SetPosition(lineRenderer.positionCount - 1, newFingerPos);

        edgeCollider.points = fingerPositions.ToArray();
    }
}
