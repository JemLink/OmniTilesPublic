using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class Pet : HandBehavior {

    // TODO: interpolate smoother between all the velocities
    // maybe change with coroutine the point to swim to every time interval instead of random value
    // then lerp between these

    
    [Header("Speed")]
    public float speed;
    public float rotationSpeed;
    public float animationSpeed;

    [Header("Range of Objects")]
    public float rangeHand;
    public float rangeBorder;
    public Collider movingZone;


    private Animator anim;

    private Vector3 randomTargetPoint = Vector3.zero;

    // Use this for initialization
    void Start () {
        StartCoroutine(ChangeTargetPoint(1.0f, 1.0f, 1.0f));
        anim = this.gameObject.GetComponentInChildren<Animator>();
    }
	
	// Update is called once per frame
	void Update () {

        if (active)
        {
            MovePet();
        }

	}

    private void MovePet()
    {
        Hand closestHand = GetNextHand();

        // if there is no hand: move randomly
        if(closestHand == null)
        {
            MoveRandom();
        }
        else
        {
            MovePetDependingOnGesture(closestHand);
        }


        //Debug.Log("Velocity: " + rigid.velocity);
        AvoidScreenBorder(rangeBorder);

        
    }




    private void MovePetDependingOnGesture(Hand hand)
    {
        switch (hand.gesture)
        {

            // we need to get the position of joint (0 is wrist) since hand position is set to zero vector
            case Hand.Gesture.Closed:
                MoveAwayFrom(hand.jointsRep[0].transform.position, rangeHand);
                break;
            case Hand.Gesture.Open:
                MoveTowards(hand.jointsRep[0].transform.position);
                break;
            default:
                break;
        }
    }


    private void MoveAwayFrom(Vector3 point, float range)
    {
        if (Vector3.Distance(transform.position, point) < range)
        {
            Vector3 direction = (transform.position - point).normalized;
            float amount = range - Vector3.Distance(transform.position, point);

            Vector3 targetPoint = transform.position + (direction * amount);
            MoveTowards(targetPoint);
        }
        else
        {
            MoveRandom();
        }
    }

    private void MoveRandom()
    {
        MoveTowards(randomTargetPoint);
    }


    private void MoveTowards(Vector3 point)
    {
        float step = speed * Time.deltaTime;

        transform.position = Vector3.MoveTowards(transform.position, point, step);

        if (anim)
        {
            anim.speed = Mathf.Max(1.0f, Vector3.Distance(transform.position, point) * animationSpeed);
        }

        Debug.DrawLine(transform.position, point, Color.magenta);

        RotateTowards(point);
    }


    private void RotateTowards(Vector3 targetPoint)
    {
        if (Vector3.Distance(transform.position, targetPoint) > 0.01)
        {
            Quaternion targetRotation = Quaternion.identity;

            float step = rotationSpeed; 
            Vector3 targetDirection = (targetPoint - transform.position).normalized;

            //Debug.Log("TargetDirection: " + targetDirection);

            targetRotation = Quaternion.LookRotation(targetDirection);
            transform.rotation = Quaternion.RotateTowards(transform.rotation, targetRotation, step);
        }



    }


    IEnumerator ChangeTargetPoint(float xRange, float yRange, float zRange)
    {
        while (true)
        {
            float x =  Random.Range(-xRange, xRange);
            float y = Random.Range(-yRange, yRange);
            float z = Random.Range(-zRange, zRange);

            randomTargetPoint = movingZone.transform.position + (new Vector3(x, y, z));

            yield return new WaitForSeconds(Random.Range(2.0f, 4.0f));
        }

    }


    
    private void AvoidScreenBorder(float range)
    {
        if(Vector3.Distance(movingZone.bounds.ClosestPoint(transform.position), transform.position) < range)
        {
            MoveAwayFrom(movingZone.bounds.ClosestPoint(transform.position), range);
        }

        if (!movingZone.bounds.Contains(transform.position))
        {
            Vector3 diff = transform.position - movingZone.bounds.ClosestPoint(transform.position);

            transform.position = movingZone.bounds.ClosestPoint(transform.position) - diff;
        }

        Debug.DrawLine(transform.position, movingZone.bounds.ClosestPoint(transform.position));

        
    }
}
