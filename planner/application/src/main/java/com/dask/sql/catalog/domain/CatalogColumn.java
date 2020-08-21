package com.dask.sql.catalog.domain;

import java.util.ArrayList;
import java.util.Collection;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Enumerated;
import javax.persistence.FetchType;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.JoinTable;
import javax.persistence.ManyToMany;
import javax.persistence.ManyToOne;
import javax.persistence.OneToOne;
import javax.persistence.Table;

/**
 * <h1>Representaion of a column in a table</h1> A {@link CatalogTable} contains several columns. The point of this
 * class is to be able to store names and types and persist these via hibernate.
 *
 * @author felipe
 *
 */
@Entity
@Table(name = "blazing_catalog_columns")
public class CatalogColumn implements Comparable {
	/**
	 * Default constructore does nothing
	 */

	public CatalogColumn() {}

	/**
	 * Create a new column from a name and a type.
	 *
	 * @param name
	 *            the name that we will give the column
	 * @param type
	 *            the {@link CatalogColumnDataType} which maps to a gdf_dtype in cuDF
	 * @param orderValue
	 *            the order that Hibernate must obey at the creation time
	 */
	public CatalogColumn(String name, CatalogColumnDataType type, int orderValue) {
		this.dataType = type;
		this.name = name;
		this.orderValue = orderValue;
	}

	/**
	 * A value generated by the database which hibernate is using to persist schemas.
	 */

	@Id @GeneratedValue @Column(name = "id") private Long id;

	/**
	 * The name of the column.
	 */
	@Column(name = "name", nullable = false) private String name;

	/**
	 * An enum type which maps to gdf_dtype in cuDF
	 */
	@Enumerated @Column(name = "data_type", columnDefinition = "smallint") private CatalogColumnDataType dataType;

	@Column(name = "order_value", nullable = false) private int orderValue;

	/**
	 * The table to which this column belongs to.
	 */
	@ManyToOne(fetch = FetchType.EAGER) @JoinColumn(name = "table_id") private CatalogTable table;

	public Long
	getId() {
		return id;
	}

	public void
	setId(Long id) {
		this.id = id;
	}

	public String
	getColumnName() {
		return this.name;
	}

	public void
	setColumnName(String name) {
		this.name = name;
	}

	public CatalogColumnDataType
	getColumnDataType() {
		return this.dataType;
	}

	public void
	setColumnDataType(CatalogColumnDataType dataType) {
		this.dataType = dataType;
	}

	public CatalogTable
	getTable() {
		return table;
	}

	public void
	setTable(CatalogTable newTable) {
		this.table = newTable;
	}

	public void
	setColumnDataType(String type) {
		this.dataType = CatalogColumnDataType.fromString(type);
	}

	public int
	getOrderValue() {
		return orderValue;
	}

	public void
	setOrderValue(int orderValue) {
		this.orderValue = orderValue;
	}

	public int
	compareTo(Object o) {
		Integer self = new Integer(this.orderValue);
		Integer other = new Integer(((CatalogColumn) o).getOrderValue());
		return self.compareTo(other);
	}
}
