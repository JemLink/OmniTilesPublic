using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PetTestMovement : MonoBehaviour
{

    public bool active;

    public float speed;
    public float range;

    public enum Gesture { open, close, other }
    public Gesture gesture;

    public Vector3 randomTargetPoint;

    public GameObject hand;


    // Use this for initialization
    void Start()
    {
        StartCoroutine(ChangeTargetPoint());
    }

    // Update is called once per frame
    void Update()
    {
        MovePet();
    }


    private void MovePet()
    {
        switch (gesture)
        {
            case Gesture.open:
                MoveToCursor();
                break;
            case Gesture.close:
                MoveAwayFromCursor(range);
                break;
            case Gesture.other:
                MoveRandom();
                break;

        }
    }


    private void MoveRandom()
    {
        MoveTowards(randomTargetPoint);
    }

    private void MoveToCursor()
    {
        MoveTowards(hand.transform.position);
    }

    private void MoveAwayFromCursor(float range)
    {
        Vector3 mousePos = hand.transform.position;

        if (Vector3.Distance(transform.position, mousePos) < range)
        {
            Vector3 direction = (transform.position - mousePos).normalized;
            float amount = range - Vector3.Distance(transform.position, mousePos);

            Vector3 targetPoint = transform.position + (direction * amount);
            MoveTowards(targetPoint);
        }
        else
        {
            MoveRandom();
        }
    }


    private void MoveTowards(Vector3 point)
    {
        float step = speed * Time.deltaTime;

        transform.position = Vector3.MoveTowards(transform.position, point, step);

        RotateTowards(point);
    }



    private void RotateTowards(Vector3 targetPoint)
    {
        if(Vector3.Distance(transform.position, targetPoint) > 0.01)
        {
            Quaternion targetRotation = Quaternion.identity;

            float step = speed; // * Time.deltaTime;
            Vector3 targetDirection = (targetPoint - transform.position).normalized;

            Debug.Log("TargetDirection: " + targetDirection);

            targetRotation = Quaternion.LookRotation(targetDirection);
            transform.rotation = Quaternion.RotateTowards(transform.rotation, targetRotation, step);
        }

        

    }


    IEnumerator ChangeTargetPoint()
    {
        while (true)
        {
            float x = Random.Range(-4.0f, 4.0f);
            float y = Random.Range(-4.0f, 4.0f);
            float z = Random.Range(-1.0f, 1.0f);

            randomTargetPoint = new Vector3(x, y, z);

            yield return new WaitForSeconds(Random.Range(2.0f, 4.0f));
        }

    }
    
}
