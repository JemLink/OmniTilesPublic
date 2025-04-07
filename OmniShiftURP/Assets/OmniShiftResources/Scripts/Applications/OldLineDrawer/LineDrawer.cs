using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public abstract class LineDrawer : MonoBehaviour
{
    [Header("Hand Representation")]
    public Hand hand;
    //public List<Vector3> fingerPositions;
    public Hand.Gesture lastGesture = Hand.Gesture.Open;

    [Header("Line Drawing")]

    public LineController lineController;

    public GameObject linePrefab;

    [Range(0.0f, 0.15f)]
    public float lineWidth = 0.1f;
    [Range(0.0f, 0.01f)]
    public float minDrawingInterval = 0.001f;
    public Color[] lineColors;
    protected int currentColorID = 0;
    
    public GameObject currentLine;

    public LineRenderer lineRenderer;


    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
