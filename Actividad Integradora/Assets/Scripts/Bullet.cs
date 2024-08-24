using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BulletMovement : MonoBehaviour
{
    public float speed = 5f; // Velocidad de la bala

    void Update()
    {
        // Mover la bala hacia adelante
        transform.Translate(Vector3.up * speed * Time.deltaTime);
    }

    void OnBecameInvisible()
    {
        // Destruir la bala cuando salga de la pantalla para no llenar la memoria
        Destroy(gameObject);
    }
}

